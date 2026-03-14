import json
import os
import sys

TEAM_DIR = ".antigravity/team"

def init_team():
    """Inicializa la infraestructura del equipo Juanka."""
    os.makedirs(f"{TEAM_DIR}/mailbox", exist_ok=True)
    os.makedirs(f"{TEAM_DIR}/locks", exist_ok=True)
    tasks_path = f"{TEAM_DIR}/tasks.json"
    if not os.path.exists(tasks_path):
        with open(tasks_path, 'w') as f:
            json.dump({"tasks": [], "members": ["Juanka", "Arquitecto", "Especialista", "Investigador", "Revisor"]}, f, indent=2)
    if not os.path.exists(f"{TEAM_DIR}/broadcast.msg"):
        with open(f"{TEAM_DIR}/broadcast.msg", 'w') as f: f.write("")
    print("OK: Infraestructura 'Equipo Juanka' lista y operativa.")

def assign_task(title, assigned_to, deps=[]):
    """Asigna una nueva tarea bajo la dirección de Juanka."""
    path = f"{TEAM_DIR}/tasks.json"
    with open(path, 'r+') as f:
        data = json.load(f)
        task = {
            "id": len(data["tasks"]) + 1,
            "title": title,
            "status": "PENDING",
            "plan_approved": False,
            "assigned_to": assigned_to,
            "dependencies": deps
        }
        data["tasks"].append(task)
        f.seek(0)
        json.dump(data, f, indent=2)
    print(f"OK: Tarea {task['id']} ({title}) asignada a {assigned_to} por orden de Juanka.")

def broadcast(sender, text):
    """Envía un mensaje global del equipo."""
    msg = {"de": sender, "tipo": "BROADCAST", "mensaje": text}
    with open(f"{TEAM_DIR}/broadcast.msg", 'a') as f:
        f.write(json.dumps(msg) + "\n")
    print(f"OK: Mensaje global enviado por {sender}.")

def send_message(sender, receiver, text):
    """Envía un mensaje al buzón de un agente."""
    msg = {"de": sender, "mensaje": text}
    with open(f"{TEAM_DIR}/mailbox/{receiver}.msg", 'a') as f:
        f.write(json.dumps(msg) + "\n")
    print(f"OK: Mensaje enviado a {receiver}.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'init': 
            init_team()
        elif cmd == 'assign' and len(sys.argv) >= 4:
            assign_task(sys.argv[2], sys.argv[3])
        elif cmd == 'broadcast' and len(sys.argv) >= 4:
            broadcast(sys.argv[2], sys.argv[3])
        elif cmd == 'send' and len(sys.argv) >= 5:
            send_message(sys.argv[2], sys.argv[3], sys.argv[4])
