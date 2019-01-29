import new_database as db

task_list = db.get_all_tasks()
print("#Tasks = ", len(task_list))