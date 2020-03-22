def load_list(filename, sep='\n', encoding='utf-8-sig'):
    # Returns a list consisting of the contents of a file separated
    # by a newline character or the specified separator
    # e.g., ',' for csv files
    with open(filename, 'rt', encoding=encoding) as f:
        raw = f.read()

    return raw.split(sep)


def deck_of_cards(suited=True, cards_per_suit=13, suits=('S', 'D', 'C', 'H')):
    """
    Generates a list containing (cards_per_suit * len(suits)) cards
    Suited determines whether a suit character (defined by the suits variable)
    is appended to the end of each card
    """
    deck = []

    for i in range(len(suits)):
        for j in range(1, cards_per_suit+1):
            if suited:
                deck.append(str(j) + suits[i])
            else:
                deck.append(str(j))
    return deck


def send_smtp_gmail(email_to, subject, msg="Default message.", login_info='email.json'):
    """
    sends an email with the relevant fields using GMail
    :param email_to: can be a single string, can be a list of strings. Must all be valid email addresses
    :param subject: subject field of the email
    :param msg: body text, can be HTML or plain text
    :param login_info: account credentials for sending email
    :return: no return value
    """
    import smtplib
    import json

    with open(login_info, 'r') as f:
        login = json.loads(f.read())

    username = login["username"]
    password = login["password"]
    smtp_server = "smtp.gmail.com:587"
    email_body = ''.join(['From: ', username, '\nSubject: ', subject, "\n", msg])

    server = smtplib.SMTP(smtp_server)
    server.starttls()
    server.login(username, password)
    server.sendmail(username, [] + email_to, email_body)
    server.quit()


def make_translation_table(filename):
    """
    Creates a dictionary containing a translation table for the specified genetic code.
    Dictionary keys are all-caps strings for each codon (e.g., 'ATG', 'GGG', 'CTC', etc)
    Example usage: table['ATG'] will return 'M' (for the standard genetic code)
    See https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi for translation tables
    :param filename: the file used to make the translation table
    :return: dictionary object with all possible translations of triplet codons
    """
    with open(filename, encoding='utf-8-sig') as f:
        raw_table = f.read()

    split_table = raw_table.split('\n')
    table = dict()

    for i in range(11, 75):
        codon = ''.join([split_table[2][i], split_table[3][i], split_table[4][i]])
        table[codon] = split_table[0][i]

    return table
