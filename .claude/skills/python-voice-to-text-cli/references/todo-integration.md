# Todo Integration Patterns for Voice-to-Text

This document covers patterns for integrating voice-to-text functionality with todo list applications.

## Natural Language Command Processing

### Command Categories
1. **Add Tasks**: "Add buy groceries", "Create task call mom"
2. **Delete/Complete Tasks**: "Mark task 1 as done", "Delete buy milk"
3. **List/View Tasks**: "Show my todos", "What's on my list"
4. **Modify Tasks**: "Update task 1 with new due date"
5. **Search Tasks**: "Find tasks with groceries"

### Command Parsing Patterns
```python
import re

def parse_todo_command(text):
    """
    Parse natural language into structured todo commands
    """
    text = text.lower().strip()

    # Add command patterns
    add_patterns = [
        r'(add|create|new|make)\s+(a\s+|an\s+|)\s*(task|todo|item|note)\s+[:\-]?\s*(.+)',
        r'(add|create|new|make)\s+(.+)\s+(to|as)\s+(a\s+|an\s+|)\s*(task|todo|item|note)',
        r'(add|create|new|make)\s+(.+)',
        r'(buy|get|purchase)\s+(.+)',
        r'(remember|remind|note)\s+(.+)',
        r'(schedule|plan)\s+(.+)'
    ]

    # Delete/Complete command patterns
    delete_patterns = [
        r'(delete|remove|done|complete|finish)\s+(task|todo|item)\s*(\d+|.+)?',
        r'(mark|set)\s+(\d+|.+)\s+(as\s+)?(done|completed|finished|deleted|removed)'
    ]

    # List command patterns
    list_patterns = [
        r'(show|list|display|view)\s+(my\s+)?(tasks|todos|items|notes)',
        r'(what|show)\s+(is\s+)?(on\s+)?(my\s+)?(list|todo|tasks)',
        r'(list|show)\s+(all\s+)?(tasks|todos|items)'
    ]

    # Process patterns
    for pattern in add_patterns:
        match = re.search(pattern, text)
        if match:
            task_desc = next((g for g in reversed(match.groups()) if g and not g.isdigit()), None)
            if task_desc:
                return {'command': 'add', 'task': task_desc.strip()}

    for pattern in delete_patterns:
        match = re.search(pattern, text)
        if match:
            target = next((g for g in reversed(match.groups()) if g and g != 'as' and g != 'done'), None)
            return {'command': 'delete', 'target': target.strip() if target else None}

    for pattern in list_patterns:
        if re.search(pattern, text):
            return {'command': 'list', 'target': None}

    # Default to add if no pattern matches
    return {'command': 'add', 'task': text}
```

## Integration with Todo List Systems

### Simple In-Memory Todo List
```python
class TodoList:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, task_text):
        task = {
            'id': self.next_id,
            'text': task_text,
            'completed': False,
            'created_at': time.time()
        }
        self.tasks.append(task)
        self.next_id += 1
        return task

    def complete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                return task
        return None

    def list_tasks(self):
        return self.tasks

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
```

### Voice Command Handler
```python
import speech_recognition as sr
import time

class VoiceTodoHandler:
    def __init__(self):
        self.todo_list = TodoList()
        self.recognizer = sr.Recognizer()

    def process_voice_command(self):
        """
        Process a single voice command and update todo list
        """
        with sr.Microphone() as source:
            print("Listening for todo command...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = self.recognizer.listen(source, timeout=5)

        try:
            # Convert speech to text
            text = self.recognizer.recognize_google(audio)
            print(f"Heard: {text}")

            # Parse the command
            command = parse_todo_command(text)

            # Execute the command
            return self.execute_command(command)

        except sr.WaitTimeoutError:
            print("No speech detected")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None

    def execute_command(self, command):
        """
        Execute the parsed command on the todo list
        """
        cmd_type = command.get('command')

        if cmd_type == 'add':
            task_text = command.get('task', '')
            task = self.todo_list.add_task(task_text)
            print(f"Added task: {task['text']}")
            return task

        elif cmd_type == 'delete':
            target = command.get('target')
            if target and target.isdigit():
                task_id = int(target)
                self.todo_list.delete_task(task_id)
                print(f"Deleted task #{task_id}")
            else:
                # Find task by text content
                for task in self.todo_list.list_tasks():
                    if target.lower() in task['text'].lower():
                        self.todo_list.delete_task(task['id'])
                        print(f"Deleted task: {task['text']}")
                        break
            return {'status': 'deleted', 'target': target}

        elif cmd_type == 'list':
            tasks = self.todo_list.list_tasks()
            print("Your tasks:")
            for task in tasks:
                status = "✓" if task['completed'] else "○"
                print(f"  {status} [{task['id']}] {task['text']}")
            return tasks

        else:
            print(f"Unknown command: {cmd_type}")
            return None
```

## Continuous Listening Mode

### For Todo Applications
```python
def continuous_todo_mode():
    """
    Continuous listening mode for ongoing todo management
    """
    handler = VoiceTodoHandler()
    print("Voice Todo Mode Started")
    print("Commands: 'add task', 'list tasks', 'mark done', etc.")
    print("Say 'quit' to exit")

    while True:
        try:
            result = handler.process_voice_command()

            # Check if user said 'quit' or similar
            if result and 'quit' in result.get('text', '').lower():
                break

        except KeyboardInterrupt:
            print("\nStopping voice todo mode...")
            break
```

## Error Handling and User Feedback

### Voice Command Validation
```python
def validate_voice_command(command):
    """
    Validate voice command before execution
    """
    if not command or 'command' not in command:
        return False, "Invalid command structure"

    cmd_type = command['command']
    if cmd_type not in ['add', 'delete', 'list']:
        return False, f"Unknown command type: {cmd_type}"

    if cmd_type == 'add' and not command.get('task'):
        return False, "No task text provided"

    return True, "Valid command"
```

### User Feedback Patterns
```python
def provide_voice_feedback(result, command_type):
    """
    Provide appropriate feedback based on command result
    """
    if result is None:
        if command_type == 'add':
            return "I couldn't add that task. Please try again."
        elif command_type == 'list':
            return "I couldn't retrieve your tasks. Please try again."
        else:
            return "I couldn't process that command. Please try again."
    else:
        if command_type == 'add':
            return f"Successfully added task: {result['text']}"
        elif command_type == 'list':
            count = len(result)
            return f"You have {count} tasks in your list."
        else:
            return "Command processed successfully."
```

## Integration with Next.js Frontend

### Data Format for Frontend
```python
def get_todo_data_for_frontend():
    """
    Format todo data for Next.js frontend consumption
    """
    tasks = self.todo_list.list_tasks()
    return {
        'tasks': [
            {
                'id': task['id'],
                'text': task['text'],
                'completed': task['completed'],
                'createdAt': task['created_at']
            }
            for task in tasks
        ],
        'total': len(tasks),
        'completed': len([t for t in tasks if t['completed']]),
        'pending': len([t for t in tasks if not t['completed']])
    }
```

### API Endpoint Pattern
```python
from flask import Flask, jsonify, request

app = Flask(__name__)
handler = VoiceTodoHandler()

@app.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify(handler.get_todo_data_for_frontend())

@app.route('/api/todos', methods=['POST'])
def add_todo_voice():
    # Expect voice data or text from voice recognition
    data = request.json
    command = parse_todo_command(data.get('text', ''))
    result = handler.execute_command(command)
    return jsonify(result)
```

## Performance Considerations

### Optimizing for Real-Time Processing
1. **Pre-process audio**: Adjust for ambient noise before each command
2. **Timeout handling**: Set appropriate timeouts to prevent hanging
3. **Command validation**: Validate commands quickly to provide fast feedback
4. **Caching**: Cache common command patterns for faster recognition