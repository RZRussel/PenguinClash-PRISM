import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.setrecursionlimit(100000)

from ABSGenerator.core.prism.expression_builder import *
from typing import Dict, Any
from copy import deepcopy
from physics import *
from generatortools import *

K_PENGUIN_X = "x1"
K_PENGUIN_Y = "y1"
K_PENGUIN_DIRECTION = "direction1"
K_PENGUIN_DEAD = "dead1"

K_SCHEDULER_LOCK = "lock"

K_PENGUIN_ACTION_MOVE = "move"
K_OPERATOR_ISLAND_COLLISION = "island_collision"

K_COMMAND_LABEL = "step"

class PGGenerator:
    def __init__(self, settings: Dict):
        self._settings = settings["settings"]

    @staticmethod
    def _precondition(action: str) -> Any:
        if action == K_PENGUIN_ACTION_MOVE:
            lock = ExpressionBuilder(Identifier(K_SCHEDULER_LOCK))
            lock.append_not()

            dead = ExpressionBuilder(Identifier(K_PENGUIN_DEAD))
            dead.append_not()

            lock.append_and(dead.expression)
            return lock.expression
        return None

    def max_x(self) -> str:
        return str(self._settings["world"]["max_x"])

    def max_y(self) -> str:
        return str(self._settings["world"]["max_y"])

    def init_x1(self) -> str:
        return str(self._settings["insertions"]["init_x1"])

    def init_y1(self) -> str:
        return self._settings["insertions"]["init_y1"]

    def init_direction1(self) -> str:
        return str(self._settings["insertions"]["init_direction1"])

    def init_x2(self) -> str:
        return str(self._settings["insertions"]["init_x2"])

    def init_y2(self) -> str:
        return str(self._settings["insertions"]["init_y2"])

    def init_direction2(self) -> str:
        return str(self._settings["insertions"]["init_direction2"])

    def move(self) -> str:
        move_offsets = radial_moves(self._settings["penguin"]["move_velocity"])
        compacted_list = compact_list_by_index(move_offsets)

        precondition = self._precondition(K_PENGUIN_ACTION_MOVE)
        guard_builder = GuardBuilder(K_COMMAND_LABEL)

        for (x, y), direction in compacted_list:
            x_cond_builder = ExpressionBuilder(Identifier(K_PENGUIN_X))

            if x >= 0:
                x_cond_builder.append_add(Integer(x))

                update_builder = UpdateBuilder(Identifier(K_PENGUIN_X), x_cond_builder.expression)

                x_cond_builder.append_le(Integer(self._settings["world"]["max_x"]))
            else:
                x_cond_builder.append_subtract(Integer(-x))

                update_builder = UpdateBuilder(Identifier(K_PENGUIN_X), x_cond_builder.expression)

                x_cond_builder.append_ge(Integer(0))

            x_cond_builder.wrap_paranthesis()

            y_cond_builder = ExpressionBuilder(Identifier(K_PENGUIN_Y))
            if y >= 0:
                y_cond_builder.append_add(Integer(y))

                update_builder.add_update(Identifier(K_PENGUIN_Y), y_cond_builder.expression)

                y_cond_builder.append_le(Integer(self._settings["world"]["max_y"]))
            else:
                y_cond_builder.append_subtract(Integer(-y))

                update_builder.add_update(Identifier(K_PENGUIN_Y), y_cond_builder.expression)

                y_cond_builder.append_ge(Integer(0))

            y_cond_builder.wrap_paranthesis()

            if precondition is not None:
                condition_builder = ExpressionBuilder(precondition)
                condition_builder.append_and(x_cond_builder.expression)
            else:
                condition_builder = ExpressionBuilder(x_cond_builder.expression)

            condition_builder.append_and(y_cond_builder.expression)

            if type(direction) == range:
                for d in direction:
                    copy_update_builder = deepcopy(update_builder)
                    copy_update_builder.add_update(Identifier(K_PENGUIN_DIRECTION), Integer(d))
                    guard_builder.add_guard(condition_builder.expression, copy_update_builder.expression)
            else:
                update_builder.add_update(Identifier(K_PENGUIN_DIRECTION), Integer(direction))
                guard_builder.add_guard(condition_builder.expression, update_builder.expression)

        return guard_builder.build()

    def island_collision(self) -> str:
        center = (self._settings["island"]["center_x"], self._settings["island"]["center_y"])
        a = self._settings["island"]["small_radius"]
        b = self._settings["island"]["big_radius"]

        move_dead_points = reachable_points_from_ellipsis(center, a, b, self._settings["penguin"]["move_velocity"])
        flash_dead_points = reachable_points_from_ellipsis(center, a, b, self._settings["penguin"]["flash_velocity"])
        compacted_points = compact_2d_points(list(move_dead_points.union(flash_dead_points)))

        or_builder = None
        for x, y in compacted_points:
            x_expr = ExpressionBuilder(Identifier(K_PENGUIN_X))
            x_expr.append_eq(Integer(x))

            y_expr = ExpressionBuilder(Identifier(K_PENGUIN_Y))

            if type(y) == range:
                copy_y_expr = deepcopy(y_expr)
                y_expr.append_ge(Integer(y[0]))
                copy_y_expr.append_le(Integer(y[-1]))
                y_expr.append_and(copy_y_expr.expression)
            else:
                y_expr.append_eq(Integer(y))

            x_expr.append_and(y_expr.expression)

            if or_builder is None:
                or_builder = ExpressionBuilder(x_expr.expression)
            else:
                or_builder.append_newline()
                or_builder.append_or(x_expr.expression)

        or_builder.wrap_paranthesis()

        return or_builder.build()
