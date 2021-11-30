"""
The MIT License (MIT)

Copyright (c) StockerMC

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, List, Optional, Dict
import os
import inspect

from .item import Item, ItemCallbackType
from .view import View
from ..enums import ComponentType
from ..utils import MISSING

if TYPE_CHECKING:
    from ..interactions import Interaction
    from ..types.interactions import InteractionModelInteractionCallbackData

class Modal(View):
    """Represents a UI modal.

    This implements similar functionality to :class:`discord.ui.View`.

    Parameters
    ----------
    timeout: Optional[:class:`float`]
        Timeout in seconds from last interaction with the UI before no longer accepting input.
        If ``None`` then there is no timeout.
    children: List[:class:`discord.ui.Item`]
        The children of the modal.
        A modal can have a maximum of 5 children.
    title: Optional[:class:`str`]
        The title of the modal, if any.
    custom_id: :class:`str`
        The ID of the modal that gets received during an interaction.
        If not given then one is generated for you.
    row: Optional[:class:`int`]
        The relative row this modal belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """

    __discord_ui_modal__: ClassVar[bool] = True

    def __init_subclass__(cls) -> None:
        children: List[ItemCallbackType] = []
        for base in reversed(cls.__mro__):
            for member in base.__dict__.values():
                if hasattr(member, '__discord_ui_model_type__'):
                    children.append(member)

        if len(children) > 5:
            raise TypeError('View cannot have more than 5 children')

        cls.__view_children_items__ = children

    def __init__(
        self,
        *,
        timeout: Optional[float] = 180,
        title: Optional[str] = None,
        custom_id: str = MISSING,
        row: Optional[int] = None,
        children: List[Item] = MISSING,
    ) -> None:
        super().__init__(timeout=timeout)
        self._provided_custom_id: bool = custom_id is not MISSING
        self.title: Optional[str] = title
        self.custom_id: str = os.urandom(16).hex() if custom_id is MISSING else custom_id
        self.row: Optional[int] = row
        if children is not MISSING:
            self.children.extend(children)

    def refresh_state(self, interaction: Interaction) -> None:
        ...

    async def callback(self, interaction: Interaction) -> None:
        ...

    def to_callback_data(self) -> Dict[str, Any]:
        payload = {
            'custom_id': self.custom_id,
            'components': self.to_components()
        }

        if self.title is not None:
            payload['title'] = self.title

        return payload

    def is_persistent(self) -> bool:
        """:class:`bool`: Whether the view is set up as persistent.

        A persistent view has all their components with a set ``custom_id`` and
        a :attr:`timeout` set to ``None``.
        """
        return self.timeout is None and self._provided_custom_id and all(item.is_persistent() for item in self.children)

    def add_item(self, item: Item[Any]) -> None:
        """Adds an item to the modal.

        Parameters
        -----------
        item: :class:`Item`
            The item to add to the modal.

        Raises
        --------
        TypeError
            An :class:`Item` was not passed.
        ValueError
            Maximum number of children has been exceeded (5)
            or the row the item is trying to be added to is full.
        """

        if len(self.children) > 5:
            raise ValueError('maximum number of children exceeded')

        if not isinstance(item, Item):
            raise TypeError(f'expected Item not {item.__class__!r}')

        self.__weights.add_item(item)

        item._view = self
        self.children.append(item)


# def modal(
#     *,
#     title: Optional[str] = None,
#     custom_id: str = MISSING,
#     row: Optional[int] = None,
#     children: List[Item],
# ) -> Callable[[ItemCallbackType], ItemCallbackType]:
#     """A decorator that attaches a modal to a component.

#     The function being decorated should have three parameters, ``self`` representing
#     the :class:`discord.ui.View`, the :class:`discord.ui.Modal` and
#     the :class:`discord.Interaction` you receive.

#     Parameters
#     ----------
#     children: List[:class:`discord.ui.Item`]
#         The children of the modal.
#         A modal can have a maximum of 5 children.
#     title: Optional[:class:`str`]
#         The title of the modal, if any.
#     custom_id: :class:`str`
#         The ID of the modal that gets received during an interaction.
#         If not given then one is generated for you.
#     row: Optional[:class:`int`]
#         The relative row this modal belongs to. A Discord component can only have 5
#         rows. By default, items are arranged automatically into those 5 rows. If you'd
#         like to control the relative positioning of the row then passing an index is advised.
#         For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
#         ordering. The row number must be between 0 and 4 (i.e. zero indexed).
#     """

#     def decorator(func: ItemCallbackType) -> ItemCallbackType:
#         if not inspect.iscoroutinefunction(func):
#             raise TypeError('modal function must be a coroutine function')

#         func.__discord_ui_model_type__ = Modal
#         func.__discord_ui_model_kwargs__ = {
#             'title': title,
#             'children': children,
#             'row': row,
#             'custom_id': custom_id,
#         }
#         return func

#     return decorator
