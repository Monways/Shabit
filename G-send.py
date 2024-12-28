import os
import random
import time
import smtplib
import string
import re
import datetime
import threading
import dns.resolver
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from transformers import pipeline

# Load the GPT-2 model
generator = pipeline('text-generation', model='gpt2')

# Semaphore for controlling concurrent threads
max_concurrent_threads = 5
semaphore = threading.Semaphore(max_concurrent_threads)

# Configuration Parameters
BCC_COUNT = 20  # Number of emails to send per batch
DOMAINS_LIST = [
    'allrecipes.com',
    'foodnetwork.com',
    'thekitchn.com',
    'seriouseats.com',
    'epicurious.com',
    'smittenkitchen.com',
    'simplyrecipes.com',
    'food.com',
    'cuisinart.com',
    'williams-sonoma.com',
    'surlatable.com',
    'oxo.com',
    'kitchenaid.com',
    'lecreuset.com',
    'calphalon.com',
    'anolon.com',
    'nordicware.com',
    'blendtec.com',
    'instantpot.com',
    'americastestkitchen.com',
    'tasteofhome.com',
    'eatingwell.com',
    'bonappetit.com',
    'savorysimple.net',
    'chefschoice.com',
    'delish.com',
    'kitchenstories.com',
    'marthastewart.com',
    'goodhousekeeping.com',
    'cookinglight.com',
    'recipecorner.com',
    'modernkitchen.com',
    'myrecipes.com',
    'thepioneerwoman.com',
    'damndelicious.net',
    'minimalistbaker.com',
    'cookieandkate.com',
    'kitchenknifereview.com',
    'tasty.co',
    'homechef.com'
]



# List of random words to replace 'contact'
RANDOM_WORDS_LIST = [
    'kitcheninfo', 'tooladmin', 'customersupport', 'prohello', 'toolnewsletter',
    'cookingtips', 'producthelp', 'kitchennews', 'chefsupport', 'gourmetguide',
    'protools', 'kitchenupdates', 'cookingsupport', 'productalerts', 'proinfo',
]


# Additional random words for subject generation
SUBJECT_WORDS_LIST = [
    "KitchenUpdate", "ImportantReminder", "ExclusiveInvitation", "ProductNewsletter", "OfficialAnnouncement",
    "SpecialOffer", "CustomerFeedback", "UserRequest", "UrgentAlert", "DetailedReport",
    "KitchenSummary", "EssentialInformation", "OrderConfirmation", "ToolProposal",
    "PolicyNotice", "ImmediateActionRequired", "FollowUpAction", "ScheduledMeeting", "CustomerQuestion",
    "ExpertInsight", "ProfessionalSuggestion", "In-DepthReview", "ApplicationStatus", "ExclusiveDeal",
    "FocusedDiscussion", "ProCookingTips", "FeatureHighlights", "CustomerSurvey",
    "QuickPoll", "ComprehensiveGuide", "ProAdvice", "KitchenResource", "NewToolLaunch",
    "MilestoneCelebration", "AchievementHighlight", "CustomerSupport", "ImmediateAction", "RequestClarification",
    "ProfessionalConnection", "ProductIntroduction", "StrategicPlan", "KitchenChecklist", "KeyInsights",
    "ProblemResolution", "TopRecommendation", "CustomerEngagement", "QuickCheckIn", "ProductExploration",
    "OngoingSupport", "FeedbackRequest", "RoutineCheckup", "CustomerInquiry", "ResourceGuide",
    "MonthlySummary", "WeeklyKitchenUpdate", "NewProductFeatures", "TeamAnnouncement", "EventDetails",
    "ProductOverview", "KitchenBreakthrough", "MarketForecast", "UrgentNotification", "TimelyUpdate",
    "LimitedOpportunity", "ProductDebrief", "VIPInvitation", "CollaborativeOpportunity", "KitchenNotification",
    "CurrentStatusUpdate", "HelpfulReminders", "DeepExploration", "ExpertDiscussion", "LatestHighlights"
]


# Function to generate random strings
def generate_random_string(length, char_type):
    char_sets = {
        'an': string.ascii_letters + string.digits,
        'n': string.digits,
        'a': string.ascii_letters
    }
    return ''.join(random.choices(char_sets[char_type], k=length))

# Function to generate an engaging From name using random names
def generate_from_name():
    base_name = random.choice(['Chef's knife', 'Emma', 'KITCHEN', 'Sophia', 'Noah', 'Hurry', 'International ', 'Cooking'])  # Add more names as needed
    if random.random() > 0.3:
        return f"{base_name}{generate_random_string(2, 'n')}"  # Adds a 2-digit random number
    else:
        return f"{base_name}_{generate_random_string(2, 'a')}"  # Adds a random 2-letter suffix

# Function to replace tags in the email body
def replace_tags(text):
    date_string = datetime.date.today().strftime('%Y-%m-%d')
    text = re.sub(r'\[mail_date\]', date_string, text)

    pattern = r'\[(an|n|a)_(\d+)\]'
    while match := re.search(pattern, text):
        char_type, length_str = match.groups()
        length = int(length_str)
        replacement = generate_random_string(length, char_type)
        text = text[:match.start()] + replacement + text[match.end():]

    return text

# Function to get MX record for a domain
def get_mx_record(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return str(mx_records[0].exchange).rstrip('.')
    except Exception as e:
        print(f"Failed to resolve MX record for {domain}: {e}")
        return None

# Function to generate a short GPT-2 text
def generate_gpt2_text(prompt, max_length=5):
    text = generator(prompt, max_length=max_length, num_return_sequences=1, truncation=True, pad_token_id=50256, max_new_tokens=max_length)[0]['generated_text'].strip()
    return text

# Function to generate a random and dynamic subject
def generate_subject_with_random_variations():
    base_subject = random.choice(SUBJECT_WORDS_LIST)  # Use a random subject word from the list
    base_subject += f" {generate_random_string(2, 'n')}" if random.random() > 0.3 else ""
    base_subject += f" {random.choice(['!', '?', '.'])}" if random.random() > 0.3 else ""
    
    return base_subject.strip()

# Function to read file content
def read_file_content(file_path, encoding='utf-8'):
    if not os.path.exists(file_path):
        sys.exit(f"Error: {file_path} does not exist")
    with open(file_path, 'r', encoding=encoding) as file:
        return file.readlines()

# Main Execution: Parsing content from header.txt and html.txt
header_lines = read_file_content('header.txt')
header_content = ''.join(replace_tags(line) for line in header_lines)

html_lines = read_file_content('html.txt')
html_content_match = re.search(r'(?s)(?<=<html>)(.*?)(?=</html>)', ''.join(html_lines))
html_content = html_content_match.group(0) if html_content_match else ""

# Combine header and HTML content
full_message = header_content + "\n\n" + html_content

# Randomly select a domain at the start
selected_domain = random.choice(DOMAINS_LIST)

# Randomize the 'From' email address
FROM_EMAIL = f"{generate_random_string(8, 'an')}@{selected_domain}"  # Randomized From email address

# Function to send emails
def send_emails(bcc_emails_array):
    if not bcc_emails_array:
        return

    # Randomly select a domain and a word for the "To" field
    selected_domain = random.choice(DOMAINS_LIST)
    random_word = random.choice(RANDOM_WORDS_LIST)
    
    domain = bcc_emails_array[0].split('@')[1]
    mx_record = get_mx_record(domain)
    if mx_record is None:
        return

    random_string = generate_random_string(10, 'n')
    random_return_path = f"{random_string}@{selected_domain}"

    msg = MIMEMultipart()
    msg['From'] = f"{generate_from_name()} <{FROM_EMAIL}>"
    msg['To'] = f'{random_word}{generate_random_string(8, "an")}@{selected_domain}'
    msg['Bcc'] = ', '.join(bcc_emails_array)
    msg['Subject'] = generate_subject_with_random_variations()  # Dynamic subject

    # Attach the full message content
    msg.attach(MIMEText(full_message, 'html'))

    # Randomize message headers
    msg['Message-ID'] = f"<{generate_random_string(20, 'an')}@{selected_domain}>"

    with semaphore:
        try:
            random_subdomain = generate_random_string(18, 'an')
            local_hostname = f'{random_subdomain}.{selected_domain}'
            with smtplib.SMTP(mx_record, local_hostname=local_hostname) as smtp_server:
                smtp_server.sendmail(random_return_path, [msg['To']] + bcc_emails_array, msg.as_string())
            print(f'Batch of {len(bcc_emails_array)} emails sent successfully with boundary: {random_string}')
        except Exception as e:
            print(f"Failed to send batch of {len(bcc_emails_array)} emails via {mx_record}... with return error: {e}")

# Main Execution to send emails
data = read_file_content('data.txt')
data_count = 0

while data_count < len(data):
    bcc_emails_array = [data[i].strip() for i in range(data_count, min(data_count + BCC_COUNT, len(data)))]
    data_count += BCC_COUNT

    threading.Thread(target=send_emails, args=(bcc_emails_array,)).start()
    
    # Wait for a random time between batches
    time.sleep(random.uniform(0.5, 3.0))
