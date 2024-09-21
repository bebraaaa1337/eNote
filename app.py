from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse

app = FastAPI()

# Настройка Jinja2 для рендеринга шаблонов
templates = Jinja2Templates(directory="templates")

# Добавляем поддержку сессий для хранения данных
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# Хранение данных в памяти
notes = []
templates_data = {}

# Функция для добавления flash-сообщений в сессию
def flash(request: Request, message: str, category: str = "info"):
    if "flash" not in request.session:
        request.session["flash"] = []
    request.session["flash"].append({"message": message, "category": category})

# Функция для извлечения flash-сообщений
def get_flashed_messages(request: Request):
    messages = request.session.pop("flash", [])
    return messages

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    template_content = request.session.get("template_content", "")
    request.session["template_content"] = ""  # Очищаем после использования
    flash_messages = get_flashed_messages(request)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "notes": notes,
        "templates": templates_data,
        "template_content": template_content,
        "flash_messages": flash_messages  # Передаем flash-сообщения в шаблон
    })

@app.post("/add_note")
async def add_note(request: Request, note_content: str = Form(...)):
    if note_content:
        notes.append(note_content)
        flash(request, "Заметка добавлена!", "success")
    else:
        flash(request, "Заметка не может быть пустой!", "danger")
    return RedirectResponse(url="/", status_code=303)

@app.post("/add_template")
async def add_template(request: Request, template_name: str = Form(...), template_content: str = Form(...)):
    if template_name and template_content:
        templates_data[template_name] = template_content
        flash(request, f'Шаблон "{template_name}" создан!', "success")
    else:
        flash(request, "Название или содержание шаблона не может быть пустым!", "danger")
    return RedirectResponse(url="/", status_code=303)

@app.get("/use_template/{template_name}")
async def use_template(request: Request, template_name: str):
    if template_name in templates_data:
        request.session["template_content"] = templates_data[template_name]
    else:
        flash(request, "Шаблон не найден!", "danger")
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
