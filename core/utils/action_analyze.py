from datetime import datetime

from aiogram.fsm.context import FSMContext

from core.data.postgres import PgSql


async def action_analyzer(
        state: FSMContext,
        db: PgSql,
        addinger: int,
        day_sent: datetime,
        group: str,
        answer: str = None,
        photo: str = None
):

    update = (await state.get_data()).get('update')
    if update:
        await db.update_ttable(answer, photo, addinger, group, update)
    else:
        await db.add_ttable(answer, photo, day_sent.date(), group, addinger)
