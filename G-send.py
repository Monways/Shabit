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
BCC_COUNT = 50  # Number of emails to send per batch
DOMAINS_LIST = [
    'cool-backgrounds.org',
    'wsulaw.com',
    'themrsbox.com',
    'cancelpage.com',
    'happyturtle.ca',
    'softactivity.com',
    'gxjbsj.com',
    'srpa.org',
    'wkf.fr',
    'sbimo.com',
    'nordjyskelejligheder.dk',
    'onlineuniversity.net',
    'atotech.com',
    'gamepreschooler.com',
    'abix.fr',
    'rhsport.pl',
    'cogizz.com',
    'zeninformatica.com',
    'cipafilter.com',
    'g32.nl',
    'za.net',
    'karmanebula.com',
    'bonusnopurchaserequired.com',
    'keycast.com',
    'go2bot.com',
    'webair.com',
    'snapfish.fr',
    'smsagencies.co.uk',
    'appendad.com',
    'pcomoney.com',
    'churchgrowth.org',
    'anadoluyakasikuryesi.com',
    'calmcdn.com',
    'agrogepaciok.it',
    'todoofeminin.com',
    'lettredesreseaux.com',
    'bestteensex.net',
    'mocean.com',
    'youload.com',
    'quickdollaracademy.com',
    'pandorajewelleryoutlets.com',
    '160tracker.com',
    'deurdrangers-shop.nl',
    'tcdn.ru',
    'severnaparkaspire.com',
    'meleahhall.com',
    'powermax-motorsport.com',
    'longfeel.com',
    'american.com',
    'ogretmenim.biz',
    'ifeng.fm',
    'highereducationarticles.com',
    'seyiyi.com',
    'person-centred-counselling.com',
    'fatstrawberry.com',
    'protechblog.com',
    'modenaradiorocity.it',
    'z51.biz',
    'yakutia.info',
    'vk.me',
    'baskid.co.uk',
    'okfree.net',
    'genderqueerid.com',
    'hercuton.nl',
    'thespafitnesscenter.com',
    'juliabloggers.com',
    'awlawyers.com',
    'stmargaretbbay.com',
    'candlelightcottages.com',
    'abctvlive.com',
    'muabancaooc.net',
    'dtlsitead.com',
    'aster.it',
    'georgesmion.com',
    'lowcostpower.com',
    'prisonnotebooks.com',
    'johnsaey.be',
    'vzkj.net',
    'pompalisap.com',
    'kartalkule.com',
    'countingpips.com',
    'fleurmusic.com',
    'vipbrands.com',
    'eaglefam.us',
    'adoos.com',
    'toughcountry.net',
    'cinnabar.cc',
    'naturalna-medicina.sk',
    'linksplash.info',
    'ttspro.com',
    'rousing.dk',
    'qkmedica.com',
    'freeconferencecallhd.com',
    'abahe.co.uk',
    'monitis.com',
    'chuyenchame.com',
    'fishingarticle.com',
    'arpnamehtaphotography.com',
    'conocophillips.com',
    'dakotaeye.com',
    'intelligentadoption.com',
    '51wasai.com',
    'camdencentreport.com',
    'isoc.si',
    'lordswitness.com',
    'sandiegocubicles.com',
    'lifecharlotte.com',
    'bethappleton.com',
    '39bencao.com',
    'pandapow.us',
    'dilw.ie',
    'spst.edu',
    'meshmixer.com',
    'exceedingexpectationsllc.com',
    'hdcore.eu',
    '4teens-serial.cz',
    'khaokhotalamok.com',
    'leylandsdm.co.uk',
    'nicenews.co.kr',
    'donberg.co.uk',
    'queenslandimages.com',
    'ecole-movie.jp',
    'topcities.com',
    'howardlindzon.com',
    'millionfareast.com',
    'shhzhiyektv.com',
    'professionalmuscle.com',
    'talkrocktome.com',
    'prestigioplaza.com',
    'platum.kr',
    'portalpublicitario.com',
    'hdcric.com',
    'whatismyip.com',
    'imb-jena.de',
    'scientificdrilling.com',
    'topwallpaperpictures.com',
    'ikea.gr',
    'biocell.ie',
    'lesmargouillats.com',
    'periodicoguama.org',
    'musicindiaonline.com',
    'indicitalia.com',
    'hotelmangalampalace.com',
    'one3ofidahorealestate.com',
    'ourpictures.com',
    'dynsite.net',
    'sonami.co.jp',
    'laconic-records.de',
    'vacationsdirect.com',
    'eu.pn',
    'sangmaestro.com',
    'rocketmatter.com',
    '114chn.com',
    'zencleanse.net',
    'mettsrv.ru',
    'birdiebikes.co.uk',
    'haninportal.com',
    'solofemaletraveler.com',
    'delinquencyrates.com',
    'season.kz',
    'japanesewords.net',
    'apssci.org',
    'batisteandassociates.com',
    'dnstechpack.com'
]


# List of random words to replace 'contact'
RANDOM_WORDS_LIST = [
    'info', 'admin', 'support', 'hello', 'newsletter',
]

# Additional random words for subject generation
SUBJECT_WORDS_LIST = [
    "Update","Reminder","Invitation","Newsletter","Announcement",
    "Opportunity","Feedback","Request","Alert","Report",
    "Summary","Information","Confirmation","Proposal",
    "Notice","ActionRequired","FollowUp","Meeting","Question",
    "Insight","Suggestion","Review","Application","Status",
    "Offer","Discussion","Tips","Highlights","Survey",
    "Poll","Guide","Advice","Resource","Launch",
    "Celebration","Milestone","Help","Action","Clarification",
    "Connection","Introduction","Strategy","Checklist","KeyPoints",
    "Resolution","Recommendation","Engagement","CheckIn","Exploration",
    "Support","FeedbackRequest","Checkup","Inquiry","ResourceGuide",
    "MonthlyReview","WeeklyUpdate","NewFeatures","TeamUpdate","EventDetails",
    "Overview","Breakthrough","Forecast","Alert","Update",
    "Opportunity","Debrief","Invitation","Collaborate","Notification",
    "StatusUpdate","Reminders","Exploration","Discussion","Highlights"
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
    base_name = random.choice(['Alex', 'Emma', 'Jack', 'Sophia', 'Noah', 'Olivia', 'William', 'Ava'])  # Add more names as needed
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
    time.sleep(random.uniform(0.3, 1.0))
