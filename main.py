import re
import json
import datetime
def invalid_use_error(command: str) -> None:
    if re.search(r'^help\s+', command) or re.fullmatch(r'add', command) or re.search(r'^end/s+', command) \
    or re.fullmatch(r'update', command) or re.fullmatch(r'mark', command) or re.fullmatch(r'delete', command) \
    or re.fullmatch(r'show', command) or re.fullmatch(r'delete_date', command) or re.fullmatch(r'sort', command):
        return True
    return False

def invalid_use_error_parameters(obj, command: str) -> bool:
    if obj is None:
        print(f"Error:Invalid use of the {command} commnad")
        return True
    return False

def index_error(index: int, len: int) -> bool:
    if index <= 0 or index > len:
        print("Error: Invalid given index")
        return True
    return False

def invalid_given_task_error(string: str) -> bool:
    if string[0] != '"' or string[len(string)-1] != '"' or len(string) == 2:
        print("Error: Invalid given task")
        return True
    return False

def invalid_given_status_error(string: str) -> bool:
    if string == 'done' or string == 'to do' or string == 'in progress':
        return False
    print("Error: Invalid given status")
    return True

def search_index(string: str) -> int:
    try:
        index = int(string)
    except ValueError:
        index = -1
    return index

def invalid_date(date: str) -> bool:
        if len(date) != 10 or date[4] != '/' or date[7] != '/' or index_error(search_index(date[:4]), 9999) \
        or index_error(search_index(date[5:7]), 12) or index_error(search_index(date[8:]), 31): 
            print("Error: Invalid given date format")
            return True
        return False

def add_task(task: dict, command: str) -> None:
    segment = re.search(r'^add\s+', command)
    command = command[segment.end():]
    if not invalid_given_task_error(command):
        command = command[1:(len(command)-1)]
        command = command.rstrip().lstrip()
        task["cnt"]+=1
        new_task = {
            'id': datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S'),
            'description': command,
            'status': 'to do',
            'created': datetime.date.today().strftime('%Y/%m/%d'),
            'edited': datetime.date.today().strftime('%Y/%m/%d')
        }
        task["tasks"].append(new_task)
        print(f'The task "{command}" is now tracked')

def update_task(task: dict, command: str) -> None:
    segment = re.search(r'^update\s+', command)
    command = command[segment.end():]
    segment = re.search(r'\s+', command)
    if invalid_use_error_parameters(segment, 'update'):
        return
    index: int = search_index(command[:segment.start()])
    if not (index_error(index) and invalid_given_task_error(command[segment.end():])):
        index-=1
        print(f'The "{task['tasks'][index]['description']}" task is now "{command[segment.end():]}"')
        task["tasks"][index]["description"] = command[segment.end():]
        task["tasks"][index]["edited"] = datetime.date.today().strftime('%Y/%m/%d')

def mark_task(task: dict, command: str) -> None:
    segment = re.search(r'^mark\s+', command)
    command = command[segment.end():]
    segment = re.search(r'\s+', command)
    if invalid_use_error_parameters(segment, 'mark'):
        return
    index = search_index(command[:segment.start()])
    if not index_error(index, task["cnt"]):
        index-=1
        if not invalid_given_status_error(command[segment.end():]):
            print(f'The "{task['tasks'][index]['description']}" task is now marked as "{command[segment.end():]}"')
            task["tasks"][index]["status"] = command[segment.end():]
            task["tasks"][index]["edited"] = datetime.date.today().strftime('%Y/%m/%d')

def delete_task(task: dict, command: str) -> None:
    segment = re.search(r"^delete\s+", command)
    index = search_index(command[segment.end():])
    if not index_error(index, task['cnt']):
        index-=1
        print(f'The "{task['tasks'][index]['description']}" task has been deleted')
        del task["tasks"][index]
        task['cnt']-=1

def show_a_type_a_task(task: dict, func, exception_message: str) -> None:
    found: bool = False
    for current_task in task["tasks"]:
        if func(current_task):
            found = True
            print('~',current_task['description'])
    if not found:
        print(exception_message)

def show_tasks(task: dict, command: str) -> None:
    segment = re.search(r'show\s+', command)
    command = command[segment.end():]
    if command == 'done':
        show_a_type_a_task(task, lambda ctask: ctask['status'] == 'done', 'There are no completed tasks in the tracking list')
        return
    elif command == 'all':
        show_a_type_a_task(task, lambda ctask: True, 'There are tasks in the tracking list')
        return
    elif command == 'to do':
        show_a_type_a_task(task, lambda ctask: ctask['status'] == 'to do', 'There are no upcoming tasks in the tracking list')
        return
    elif command == 'in progress':
        show_a_type_a_task(task, lambda ctask: ctask['status']== 'in progress', 'There are no in progress tasks in the tracking list')
        return
    elif command[0] >= '0' and command[0] <= '9':
        segment = re.search(r'\s+', command)
        if invalid_use_error_parameters(segment, 'show'):
            return
        given_status: str = command[segment.end():]
        given_date: str = command[:segment.start()]
        if invalid_date(given_date):
            return
        if given_status == 'done':
            show_a_type_a_task(task, lambda ctask: ctask['status'] == given_status and ctask['edited'] == given_date, "There are no \
            completed tasks in the tracking list at the given date")
            return
        elif given_status == 'to do':
            show_a_type_a_task(task, lambda ctask: ctask['status'] == given_status and ctask['edited'] == given_date, "There are no \
            upcoming tasks in the tracking list at the given date")
            return
        elif given_status == 'in progress':
            show_a_type_a_task(task, lambda ctask: ctask['status'] == given_status and ctask['edited'] == given_date, "There are no \
            in progress tasks in the tracking list at the given date")
            return
    print("Error: Invalid given show parameters")

def delete_tasks_by_date(task: dict, command: str) -> None:
    segment = re.search(r'delete_date\s+', command)
    command = command[segment.end():]
    segment = re.search(r'\s+', command)
    if invalid_use_error_parameters(segment, 'delete_date'):
        return
    given_status: str = command[segment.end():]
    given_date: str = command[:segment.start()]
    if invalid_date(given_date):
        return
    if not (given_status == 'done' or given_status == 'to do' or given_status == 'in progress' or given_status == 'all'):
        print("Error: Invalid given delete_date second parameter")
        return 
    
    index: int = task['cnt']-1
    while index >= 0:
        if (task['tasks'][index]['status'] == given_status or given_status == 'all') and task['tasks'][index]['edited'] == given_date:
            print(f'The task "{task["tasks"][index]['description']}" has been deleted')
            del task['tasks'][index]
            task['cnt']-=1
        index-=1

def sort_by_cond(task: dict, cond) -> None:
    for ind1 in range(0, task['cnt']-1):
        for ind2 in range(ind1, task['cnt']):
            if cond(task['tasks'][ind1], task['tasks'][ind2]):
                aux: dict = task['tasks'][ind1].copy()
                task['tasks'][ind1] = task['tasks'][ind2].copy()
                task['tasks'][ind2] = aux

def sort_tasks(task: dict, command: str) -> None:
    segment = re.search(r'sort\s+', command)
    command = command[segment.end():]
    if command == 'lex':
        sort_by_cond(task, lambda task1, task2: task1['description'] > task2['description'])
    elif command == 'date':
        sort_by_cond(task, lambda task1, task2: task1['edited'] > task2['edited'])
    else:
        print("Error: Invalid given parameter")

def main() -> None:
    task = {}
    f = open('commands.txt', 'r')
    commands_description: str = f.read()
    f.close()
    end_program: bool = False
    try:
        with open("tracker.json", 'r') as f:
            task = json.load(f)
    except FileNotFoundError:
        with open("tracker.json", "w") as f:
            task = {
                "cnt": 0,
                "tasks": []
            }
            json.dump(task, f, indent=3)

    with open("tracker.json", 'w') as f:
        while not end_program:
            command: str = input("task-cli ")
            command = command.strip().lstrip()
            if invalid_use_error(command):
                print("Error: Invalid use of the commnad")

            elif re.fullmatch(r'end', command):
                end_program = True

            elif re.search(r'^add\s', command):
                add_task(task, command)

            elif re.fullmatch(r'help', command):
                print(commands_description)

            elif re.search(r'^update\s', command):
                update_task(task, command)

            elif re.search(r'^mark\s', command):
                mark_task(task, command)

            elif re.search(r'^delete\s', command):
                delete_task(task, command)

            elif re.search(r'^show\s', command):
                show_tasks(task, command)

            elif re.search(r'^delete_date\s', command):
                delete_tasks_by_date(task, command)

            elif re.search(r'sort\s', command):
                sort_tasks(task, command)

            else:
                print("Error: Unrecognised command")
        json.dump(task, f, indent=3)

if __name__ == '__main__':
    main()