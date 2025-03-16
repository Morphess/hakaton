from django.shortcuts import render, redirect
from .forms import PDFUploadForm
from .models import PDFDocument
import fitz
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PDFUploadForm, ChatMessageForm
from .models import PDFDocument, ChatMessage
from datetime import datetime

@login_required
def upload_pdf(request):
    pdf_text = ""  # Змінна для тексту PDF, яку будемо передавати в шаблон
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_document = form.save()

            # Перевіряємо, чи це PDF файл
            if not pdf_document.file.name.endswith('.pdf'):
                form.add_error('file', 'Будь ласка, завантажте файл PDF.')
                return render(request, 'upload_pdf.html', {'form': form, 'pdf_text': pdf_text})

            # Отримуємо текст з PDF після завантаження
            try:
                pdf_path = pdf_document.file.path
                text = extract_text_from_pdf(pdf_path)
                pdf_text = text  # Зберігаємо текст для відображення на сторінці
            except Exception as e:
                form.add_error('file', 'Помилка при обробці PDF файлу.')
                return render(request, 'upload_pdf.html', {'form': form, 'pdf_text': pdf_text})

            return render(request, 'upload_pdf.html', {'form': form, 'pdf_text': pdf_text})  # Відображаємо на тій самій сторінці
    else:
        form = PDFUploadForm()

    return render(request, 'upload_pdf.html', {'form': form, 'pdf_text': pdf_text})

def chat(request):
    braille_code = None
    latest_message = None
    braille_input = None
    braille_input_timestamp = None
    form = ChatMessageForm()  # Ініціалізація форми за замовчуванням
    if request.method == 'POST':
        if 'message' in request.POST:
            form = ChatMessageForm(request.POST)
            if form.is_valid():
                message = form.save()
                braille_code = text_to_braille(message.message)
                latest_message = message

                # Видалення старих повідомлень, якщо їх більше 5
                messages = ChatMessage.objects.filter(message__isnull=False).order_by('-timestamp')
                if messages.count() > 5:
                    for msg in messages[5:]:
                        msg.delete()
        elif 'braille_input' in request.POST:
            braille_input = request.POST['braille_input']
            braille_input = braille_to_text(braille_input)
            braille_input_timestamp = datetime.now().strftime("%B %d, %Y, %I:%M %p")
            # Зберігаємо перекладене повідомлення як нове повідомлення
            message = ChatMessage(message=braille_input)
            message.save()
            latest_message = message
    else:
        form = ChatMessageForm()
    messages = ChatMessage.objects.filter(message__isnull=False).order_by('-timestamp')[:5]
    return render(request, 'chat.html', {'form': form, 'messages': messages, 'braille_code': braille_code, 'latest_message': latest_message, 'braille_input': braille_input, 'braille_input_timestamp': braille_input_timestamp})

def extract_text_from_pdf(pdf_path):
    """Функція для витягування тексту з PDF файлу"""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += f"\n\n---- Сторінка {page_num + 1} ----\n"
        text += page.get_text("text")  # Отримуємо текст із сторінки
    return text

def pdf_list(request):
    pdfs = PDFDocument.objects.all()
    return render(request, 'pdf_list.html', {'pdfs': pdfs})

# Функція для конвертації PDF в текст
def convert_pdf_to_text(request, pdf_id):
    try:
        # Отримуємо документ
        pdf_document = PDFDocument.objects.get(id=pdf_id)

        # Зчитуємо текст з PDF
        pdf_path = pdf_document.file.path
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += f"\n\n---- Сторінка {page_num + 1} ----\n"
            text += page.get_text("text")

        # Зберігаємо текст у базі даних
        pdf_document.text = text
        pdf_document.save()

        # Перенаправляємо на сторінку списку PDF
        return redirect('pdf_list')
    except PDFDocument.DoesNotExist:
        return redirect('pdf_list')  # Якщо документ не знайдений, редірект на список PDF
    

def delete_pdf(request, pdf_id):
    try:
        pdf = PDFDocument.objects.get(id=pdf_id)
        pdf.delete()
    except PDFDocument.DoesNotExist:
        pass
    return redirect('pdf_list')


def text_to_braille(text):
    BRAILLE_CODE_DICT = {
        'A': '⠁', 'B': '⠃', 'C': '⠉', 'D': '⠙', 'E': '⠑', 'F': '⠋', 'G': '⠛', 'H': '⠓',
        'I': '⠊', 'J': '⠚', 'K': '⠅', 'L': '⠇', 'M': '⠍', 'N': '⠝', 'O': '⠕', 'P': '⠏',
        'Q': '⠟', 'R': '⠗', 'S': '⠎', 'T': '⠞', 'U': '⠥', 'V': '⠧', 'W': '⠺', 'X': '⠭',
        'Y': '⠽', 'Z': '⠵', '1': '⠼⠁', '2': '⠼⠃', '3': '⠼⠉', '4': '⠼⠙', '5': '⠼⠑',
        '6': '⠼⠋', '7': '⠼⠛', '8': '⠼⠓', '9': '⠼⠊', '0': '⠼⠚', ',': '⠂', '.': '⠲',
        '?': '⠦', '/': '⠌', '-': '⠤', '(': '⠷', ')': '⠾', ' ': ' ',
        'А': '⠁', 'Б': '⠃', 'В': '⠺', 'Г': '⠛', 'Ґ': '⠣', 'Д': '⠙', 'Е': '⠑', 'Є': '⠡',
        'Ж': '⠚', 'З': '⠵', 'И': '⠊', 'І': '⠊', 'Ї': '⠔', 'Й': '⠽', 'К': '⠅', 'Л': '⠇',
        'М': '⠍', 'Н': '⠝', 'О': '⠕', 'П': '⠏', 'Р': '⠗', 'С': '⠎', 'Т': '⠞', 'У': '⠥',
        'Ф': '⠋', 'Х': '⠓', 'Ц': '⠉', 'Ч': '⠟', 'Ш': '⠱', 'Щ': '⠭', 'Ь': '⠮', 'Ю': '⠳',
        'Я': '⠫'
    }
    braille_code = ''.join(BRAILLE_CODE_DICT.get(char.upper(), '') for char in text)
    return braille_code

def braille_to_text(braille_code):
    BRAILLE_CODE_DICT = {
        '⠁': 'A', '⠃': 'B', '⠉': 'C', '⠙': 'D', '⠑': 'E', '⠋': 'F', '⠛': 'G', '⠓': 'H',
        '⠊': 'I', '⠚': 'J', '⠅': 'K', '⠇': 'L', '⠍': 'M', '⠝': 'N', '⠕': 'O', '⠏': 'P',
        '⠟': 'Q', '⠗': 'R', '⠎': 'S', '⠞': 'T', '⠥': 'U', '⠧': 'V', '⠺': 'W', '⠭': 'X',
        '⠽': 'Y', '⠵': 'Z', '⠼⠁': '1', '⠼⠃': '2', '⠼⠉': '3', '⠼⠙': '4', '⠼⠑': '5',
        '⠼⠋': '6', '⠼⠛': '7', '⠼⠓': '8', '⠼⠊': '9', '⠼⠚': '0', '⠂': ',', '⠲': '.',
        '⠦': '?', '⠌': '/', '⠤': '-', '⠷': '(', '⠾': ')', ' ': ' ',
        '⠁': 'А', '⠃': 'Б', '⠺': 'В', '⠛': 'Г', '⠣': 'Ґ', '⠙': 'Д', '⠑': 'Е', '⠡': 'Є',
        '⠚': 'Ж', '⠵': 'З', '⠊': 'И', '⠊': 'І', '⠔': 'Ї', '⠽': 'Й', '⠅': 'К', '⠇': 'Л',
        '⠍': 'М', '⠝': 'Н', '⠕': 'О', '⠏': 'П', '⠗': 'Р', '⠎': 'С', '⠞': 'Т', '⠥': 'У',
        '⠋': 'Ф', '⠓': 'Х', '⠉': 'Ц', '⠟': 'Ч', '⠱': 'Ш', '⠭': 'Щ', '⠮': 'Ь', '⠳': 'Ю',
        '⠫': 'Я'
    }
    text = ''.join(BRAILLE_CODE_DICT.get(char, '') for char in braille_code)
    return text