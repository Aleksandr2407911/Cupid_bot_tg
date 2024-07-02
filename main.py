import logging
import asyncio
from aiogram import Bot, Dispatcher
import user_module
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from identifications import bot_token

#функция конфигурирования и запуска бота
async def main():

    #регистрируем бота и диспетчер
    bot = Bot(token= bot_token) # vera's_cupid_bot 
    dp = Dispatcher()
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    #scheduler.add_job(user_module.send_message, trigger='date', run_date = datetime.now() + timedelta(seconds=5), 
                      #kwargs={'bot':bot})
    scheduler.add_job(user_module.send_message, trigger='cron', hour = 6, 
                      start_date = datetime.now(),
                      kwargs={'bot':bot})
    scheduler.start()
    # регистрируем роутеры в диспетчер
    # dp.include_router(admin_module.router)
    dp.include_router(user_module.router)

    #пропускаем накопившиемя апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    print('Запуск прошел успешно')
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())

