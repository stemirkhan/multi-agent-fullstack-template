from __future__ import annotations

import ast
from pathlib import Path
import re
import unittest
from unittest.mock import AsyncMock, Mock


EXAMPLE = (
    Path(__file__).resolve().parents[1]
    / ".agents/skills/unit-of-work/references/async-sqlalchemy-example.md"
)


def load_adapter(writer: Mock) -> type:
    """Execute the documented adapter with fake infrastructure dependencies."""
    classes = [
        node
        for block in re.findall(r"```python\n(.*?)\n```", EXAMPLE.read_text(), re.DOTALL)
        for node in ast.parse(block).body
        if isinstance(node, ast.ClassDef)
        and node.name == "SqlAlchemyUserWriteUnitOfWork"
    ]
    if len(classes) != 1:
        raise AssertionError("Expected exactly one documented SQLAlchemy UoW adapter")
    module = ast.Module(
        body=[
            ast.ImportFrom(
                module="__future__",
                names=[ast.alias(name="annotations")],
                level=0,
            ),
            classes[0],
        ],
        type_ignores=[],
    )
    namespace = {
        "UserWriteUnitOfWork": object,
        "SqlAlchemyUserWriter": writer,
    }
    exec(compile(ast.fix_missing_locations(module), str(EXAMPLE), "exec"), namespace)
    return namespace["SqlAlchemyUserWriteUnitOfWork"]


class UnitOfWorkExampleTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.transaction = Mock(is_active=True)
        self.transaction.commit = AsyncMock(side_effect=self.finish_transaction)
        self.transaction.rollback = AsyncMock(side_effect=self.finish_transaction)
        self.session = Mock(
            begin=AsyncMock(return_value=self.transaction),
            close=AsyncMock(),
        )
        self.writer = Mock()
        self.session_factory = Mock(return_value=self.session)
        self.uow = load_adapter(self.writer)(self.session_factory)

    def finish_transaction(self) -> None:
        self.transaction.is_active = False

    def assert_released(self) -> None:
        self.session.close.assert_awaited_once_with()
        self.assertIsNone(self.uow._session)
        self.assertIsNone(self.uow._transaction)

    async def test_exit_without_commit_rolls_back_and_closes_session(self) -> None:
        async with self.uow as entered:
            self.assertIs(entered, self.uow)
            self.assertIs(self.uow.users, self.writer.return_value)
            self.session_factory.assert_called_once_with()
            self.session.begin.assert_awaited_once_with()
            self.writer.assert_called_once_with(self.session)
            self.session.close.assert_not_awaited()

        self.transaction.commit.assert_not_awaited()
        self.transaction.rollback.assert_awaited_once_with()
        self.assert_released()

    async def test_explicit_commit_does_not_roll_back_on_exit(self) -> None:
        async with self.uow:
            await self.uow.commit()

        self.transaction.commit.assert_awaited_once_with()
        self.transaction.rollback.assert_not_awaited()
        self.assert_released()

    async def test_exception_in_context_rolls_back_and_closes_session(self) -> None:
        error = RuntimeError("use case failed")
        with self.assertRaises(RuntimeError) as caught:
            async with self.uow:
                raise error

        self.assertIs(caught.exception, error)
        self.transaction.commit.assert_not_awaited()
        self.transaction.rollback.assert_awaited_once_with()
        self.assert_released()

    async def test_begin_failure_closes_session(self) -> None:
        error = RuntimeError("begin failed")
        self.session.begin.side_effect = error
        with self.assertRaises(RuntimeError) as caught:
            await self.uow.__aenter__()

        self.assertIs(caught.exception, error)
        self.writer.assert_not_called()
        self.transaction.rollback.assert_not_awaited()
        self.assert_released()

    async def test_repository_failure_rolls_back_and_closes_session(self) -> None:
        error = RuntimeError("repository initialization failed")
        self.writer.side_effect = error
        with self.assertRaises(RuntimeError) as caught:
            await self.uow.__aenter__()

        self.assertIs(caught.exception, error)
        self.transaction.rollback.assert_awaited_once_with()
        self.assert_released()

    async def test_repository_and_rollback_failure_still_closes_session(self) -> None:
        repository_error = RuntimeError("repository initialization failed")
        rollback_error = RuntimeError("rollback failed")
        self.writer.side_effect = repository_error
        self.transaction.rollback.side_effect = rollback_error
        with self.assertRaises(RuntimeError) as caught:
            await self.uow.__aenter__()

        self.assertIs(caught.exception, rollback_error)
        self.assertIs(caught.exception.__context__, repository_error)
        self.transaction.rollback.assert_awaited_once_with()
        self.assert_released()


if __name__ == "__main__":
    unittest.main()
