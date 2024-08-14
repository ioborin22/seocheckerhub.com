from django.shortcuts import render, redirect
from urllib.parse import quote, unquote, urlparse
import requests
from bs4 import BeautifulSoup
from django.utils.translation import gettext as _

# Функция для стандартизации URL
def normalize_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = 'https://' + url
    elif parsed_url.scheme not in ['http', 'https']:
        return None  # Неподдерживаемый протокол
    return url

def check_status(response):
    status_code = response.status_code
    
    if 100 <= status_code < 200:
        icon = "ℹ️"
        status_text = _("Informational Response")
    elif 200 <= status_code < 300:
        icon = "✅"
        status_text = "OK"
        is_status_code_valid = True
    elif 300 <= status_code < 400:
        icon = "⚠️"
        status_text = _("Redirect")
    elif 400 <= status_code < 500:
        icon = "🚫"
        status_text = _("Error")
    elif 500 <= status_code < 600:
        icon = "❌"
        status_text = _("Server Error")
    else:
        icon = "❓"
        status_text = _("Unknown")
        
    recommendation = _(
        "HTTP response status codes indicate whether a specific HTTP request has been successfully completed. "
        "Responses are grouped into five classes:\n\n"
        "<ul>"
        "<li>ℹ️ Informational responses (100–199)</li>"
        "<li>✅ Successful responses (200–299)</li>"
        "<li>⚠️ Redirections (300–399)</li>"
        "<li>🚫 Client errors (400–499)</li>"
        "<li>❌ Server errors (500–599)</li>"
        "</ul>"
    )

    return {
        'info': f"{status_code} {status_text}",
        'recommendation': recommendation,
        'icon': icon,
    }


def check_page_size(response):
    page_size_kb = len(response.content) / 1024
    page_size_mb = page_size_kb / 1024
    is_size_valid = page_size_mb <= 2

    if is_size_valid:
        icon = "✅"
        size_display = f"{round(page_size_kb, 2)} KB"
        recommendation = _("The page size is optimal and within the recommended limit of 2 MB.")
    else:
        icon = "❌"
        size_display = f"{round(page_size_mb, 2)} MB"
        recommendation = _("The page size exceeds the recommended limit of 2 MB. Consider reducing the size for better performance.")

    return {
        'size_display': size_display,
        'recommendation': recommendation,
        'icon': icon,
        'is_size_valid': is_size_valid,
    }




def check_title(soup):
    title = soup.title.string if soup.title else None
    
    # Проверка существования тега <title>
    if title:
        is_title_exist = True
    else:
        title = _("No title found")
        is_title_exist = False
    
    title_length = len(title)
    
    # Определение иконки для проверки длины тега <title>
    if 35 <= title_length <= 65:
        icon = "✅"  # Галочка, если длина тега в пределах нормы
    else:
        icon = "❌"  # Крестик, если длина тега выходит за пределы нормы
    
    # Определение иконки для проверки существования тега <title>
    if not is_title_exist:
        is_title_valid_icon = "❌"  # Крестик, если тег отсутствует
    elif 35 <= title_length <= 65:
        is_title_valid_icon = "✅"  # Галочка, если длина тега в пределах нормы
    else:
        is_title_valid_icon = "⚠️"  # Треугольник, если длина тега выходит за пределы нормы
    
    title_display = f"{title}"

    title_length_display = f"<span class='text-sm text-gray-600'>{title_length} {_('characters')} (Recommended: 35-65 characters)</span>"

    recommendation = _(
        "The title length should be between 35 and 65 characters for optimal SEO performance. "
        "The meta title is an HTML tag that defines the title of your page. "
        "This tag displays your page title in search engine results, at the top of a user's browser, and also when your page is bookmarked in a list of favorites.\n\n"
        "Titles are critical to giving users a quick insight into the content of a result and why it's relevant to their query. "
        "It's often the primary piece of information used to decide which result to click on, so it's important to use high-quality titles on your web pages. "
        "Avoid too short and too long or verbose titles, which are likely to get truncated when they show up in the search results. "
        '<a href="https://support.google.com/webmasters/answer/35624" target="_blank" class="text-blue-500 hover:underline">Learn more on how to create good title tags using this Google guide.</a>'
    )

    return {
        'title_display': title_display,
        'recommendation': recommendation,
        'title_length': title_length_display,
        'icon': icon,
        'is_title_valid': 35 <= title_length <= 65,
        'is_title_exist': is_title_exist,
        'is_title_valid_icon': is_title_valid_icon,
    }





def check_description(soup):
    description = soup.find("meta", attrs={"name": "description"})
    
    # Проверка существования описания
    if description:
        description_content = description["content"]
        is_description_exist = True
    else:
        description_content = _("No description found")
        is_description_exist = False
    
    description_length = len(description_content)
    
    # Определение иконки для проверки длины описания
    if 70 <= description_length <= 320:
        icon = "✅"  # Галочка, если длина описания в пределах нормы
    else:
        icon = "❌"  # Крестик, если длина описания выходит за пределы нормы
    
    # Определение иконки для проверки существования описания
    if not is_description_exist:
        is_description_valid_icon = "❌"  # Крестик, если описание отсутствует
    elif 70 <= description_length <= 320:
        is_description_valid_icon = "✅"  # Галочка, если длина описания в пределах нормы
    else:
        is_description_valid_icon = "⚠️"  # Треугольник, если длина описания выходит за пределы нормы
    
    description_display = f"{description_content}"

    description_length_display = f"<span class='text-sm text-gray-600'>{description_length} {_('characters')} (Recommended: 70-320 characters)</span>"

    recommendation = _(
        "The description length should be between 70 and 320 characters for optimal SEO performance. "
        "Google will sometimes use the description tag from a page to generate a search results snippet. "
        "A meta description tag should generally inform and interest users with a short, relevant summary of what a particular page is about. "
        "This is like a pitch that convinces users that the page is exactly what they're looking for. "
        '<a href="https://support.google.com/webmasters/answer/35624" target="_blank" class="text-blue-500 hover:underline">Learn more on how to create a good meta description tag, using this Google guide.</a>'
    )

    return {
        'description_display': description_display,
        'recommendation': recommendation,
        'description_length': description_length_display,
        'icon': icon,
        'is_description_valid': 70 <= description_length <= 320,
        'is_description_exist': is_description_exist,
        'is_description_valid_icon': is_description_valid_icon,
    }





def check_h1(soup, title):
    h1_tags = soup.find_all('h1')
    h1_count = len(h1_tags)
    
    # Если тегов H1 нет, возвращаем соответствующую информацию
    if h1_count == 0:
        icon_h1_exists = "❌"
        h1_display = _("No H1 tag found")
        recommendation = _("Ensure there is at least one H1 tag on the page. The H1 tag helps search engines and users understand the main content of the page.")
        return {
            'h1_display': h1_display,
            'icon_h1_exists': icon_h1_exists,
            'is_h1_valid': False,
            'recommendation': recommendation,
        }

    # Если H1 теги найдены, формируем информацию по каждому тегу
    h1_info = []
    all_checks_passed = True
    at_least_one_check_failed = False
    for i, h1 in enumerate(h1_tags):
        h1_text = h1.get_text().strip()
        h1_length = len(h1_text)
        h1_matches_title = h1_text == title

        length_check = 5 <= h1_length <= 70
        match_check = not h1_matches_title

        if not (length_check and match_check and h1_count == 1):
            at_least_one_check_failed = True

        all_checks_passed = all_checks_passed and (length_check and match_check and h1_count == 1)

        h1_info.append({
            'h1_text': h1_text,
            'h1_count_display': f"{i + 1} {_('H1 tag')}",
            'icon_h1_length': "✅" if length_check else "❌",
            'h1_length_display': f"{h1_length} {_('characters')} (Recommended: 5-70 characters)",
            'icon_h1_match': "❌" if h1_matches_title else "✅",
            'h1_match_display': _("Matches Title") if h1_matches_title else _("Does not match Title"),
        })

    # Определение значения иконки
    if all_checks_passed:
        icon_h1_exists = "✅"
    elif at_least_one_check_failed:
        icon_h1_exists = "⚠️"
    else:
        icon_h1_exists = "❌"
    
    recommendation = _(
        "Ensure there is exactly one H1 tag on the page. The H1 tag should be between 5 and 70 characters long. "
        "The H1 should summarize the content of the page, but it should not be an exact match of the title. "
        "Having a unique H1 helps search engines and users understand the main content of the page."
    )
    
    return {
        'h1_info': h1_info,
        'icon_h1_exists': icon_h1_exists,
        'is_h1_valid': True,
        'recommendation': recommendation,
    }


# Основная функция анализа SEO
def seo_analysis(url):
    try:
        response = requests.get(url, allow_redirects=False, timeout=10)
        status_data = check_status(response)
    except requests.exceptions.Timeout:
        return {'error': _("The request timed out after 10 seconds. Please try again.")}
    except requests.exceptions.RequestException as e:
        return {'error': _(f"Error requesting page: {e}")}

    soup = BeautifulSoup(response.content, 'html.parser')

    title_data = check_title(soup)
    description_data = check_description(soup)
    page_size_data = check_page_size(response)
    h1_data = check_h1(soup, title_data['title_display'])

    return {
        'status_data': status_data,
        'page_size_data': page_size_data,
        'title_data': title_data,
        'description_data': description_data,
        'h1_data': h1_data,
    }

# Основная функция обработки запросов на индексную страницу
def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            # Нормализуем URL перед кодированием
            normalized_url = normalize_url(url)
            if not normalized_url:
                results = {'error': _('Invalid URL format.')}
                return render(request, 'checker/index.html', {'results': results})

            # Кодируем URL и перенаправляем на новый путь с параметром запроса
            quoted_url = quote(normalized_url, safe=':/')
            return redirect(f'/analyze?url={quoted_url}')
        else:
            results = {'error': _('Please enter a URL.')}
            return render(request, 'checker/index.html', {'results': results})

    return render(request, 'checker/index.html')

# Функция обработки запросов на анализ URL
def url_analysis(request):
    url = request.GET.get('url')
    if url:
        decoded_url = unquote(url)
        results = seo_analysis(decoded_url)
        return render(request, 'checker/index.html', {'results': results, 'analyzed_url': decoded_url})
    else:
        results = {'error': _('No URL provided for analysis.')}
        return render(request, 'checker/index.html', {'results': results})