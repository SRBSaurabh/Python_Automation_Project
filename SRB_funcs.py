import os
import sqlite3
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import colorama
import cv2
import openpyxl
import pytesseract
from PIL import Image
from colorama import Fore, Back, Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

dtStamp = datetime.now().strftime("%d-%m-%Y  %H:%M:%S")
lots, lot_names, cells = [], [], []
w8 = 0  # as waiting GATE 0-Close; 1-Open; 9-Destroy & Exit the code
verify = []  # Totality check for 20,000 rupee lot
verified = ''  # To show totality checks to User
a, b, installments_total = None, None, 0  # As First & Second Installments nickname
acc, inst, inst_verify = [], [], []  # As First & Second Installments nickname
lot_lis, inst_no, browser = None, None, 0


# Getting Id & Password...
wbk = openpyxl.load_workbook(r"Portal.xlsx", read_only=True, data_only=True)
sheet = wbk["Summary"]
Pass = sheet['J1'].value
ID = sheet['Z1'].value
wbk.close()


def ColoredPrint(msg, color):
    colorama.init(autoreset=True)

    return (f"{color}{Style.BRIGHT}\n\n"
            "---------*********************************************************************************-----------\n\n"
            f"{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}                       {msg}                  \n\n"
            f"{color}{Style.BRIGHT}"
            f"---------********************************************************************************-----------\n\n")


# ----------------------------------------------------------------------------------------------------------------------

def recCaptcha(img_path):
    # Read image with opencv
    img = cv2.imread(img_path)
    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("clear.png", img)
    result = pytesseract.image_to_string(Image.open("clear.png"))
    os.remove("clear.png")
    return result[:6]


# --------------------------------------------------------------------------------------------------------------------

def frontEnd():
    """Taking User inputs via FrontEnd"""

    def onClick():
        global lot_lis, inst_no
        lot_lis = entry1.get()
        inst_no = v.get()

        label3 = tk.Label(root, text=" Let's Go...!!!", font=('helvetica', 15), bg='yellow', fg='#f00')
        canvas1.create_window(650, 250, window=label3)

        root.quit()

    def onPress(event):
        print("You hit ENTER.")
        onClick()

    root = tk.Tk()
    root.title('Created by SRBSaurabh  😎')
    root.iconbitmap('icon.ico')

    canvas1 = tk.Canvas(root, width=850, height=300, relief='raised', bg='#60408E')
    canvas1.pack()

    label1 = tk.Label(root, text='  *  India Post Virtual Agent  *  ', bg='#FF344C')
    label1.config(font=('helvetica', 14))
    canvas1.create_window(400, 25, window=label1)

    label2 = tk.Label(root, text='Enter the "Space" Separated LOT Numbers below: ', bg='#E6FF33')
    label2.config(font=('helvetica', 25))
    canvas1.create_window(400, 100, window=label2)

    # entry box
    entry1 = tk.Entry(root, font=('calibre', 35, 'normal'))
    canvas1.create_window(400, 170, window=entry1)

    button1 = tk.Button(text='START', command=onClick, bg='#45FF00', fg='red',
                        font=('helvetica', 20, 'bold'))
    canvas1.create_window(420, 250, window=button1)

    # Tkinter string variable able to store any string value
    v = tk.StringVar(root, "1")

    # # # Style class to add style to Radiobutton it can be used to style any ttk widget
    style = ttk.Style(root)
    style.configure("TRadiobutton", background="#00FFFF", foreground="red", font=("arial", 30, "bold"))

    ttk.Radiobutton(root, text=" 1st  Installment", variable=v, value=1).pack(side=tk.TOP, ipady=5)
    ttk.Radiobutton(root, text=" 2nd Installment", variable=v, value=2).pack(side=tk.TOP, ipady=5)

    root.bind('<Return>', onPress)
    tk.mainloop()
    return inst_no, lot_lis


# ---------------------------------------------------------------------------------------------------------------------

def portal_Login(identity=ID, password=Pass, headless=1):
    """Opening WebPortal"""
    global w8, browser, dtStamp
    chrome_path = os.getcwd()

    option = Options()
    preferences = {"download.default_directory": chrome_path, "safebrowsing.enabled": "false"}  # Chrome download Path
    option.add_experimental_option("prefs", preferences)
    option.add_argument("--log-level=3")
    if headless:
        option.add_argument("--headless")  # =========to make headless
    option.add_argument("--window-size=1280,720")

    url = 'https://dopagent.indiapost.gov.in/corp/AuthenticationController?FORMSGROUP_ID__=AuthenticationFG' \
          '&__START_TRAN_FLAG__=Y&__FG_BUTTONS__=LOAD&ACTION.LOAD=Y&AuthenticationFG.LOGIN_FLAG=3&BANK_ID=DOP' \
          '&AGENT_FLAG=Y '
    try:
        browser = webdriver.Chrome(options=option)
        browser.get(url)
        print(ColoredPrint('Opening India Post in Background.....', Fore.LIGHTBLUE_EX))
    except Exception as eo:
        print(ColoredPrint('Internet Problem\n\n --> >' + str(eo), Fore.LIGHTRED_EX))
        time.sleep(5)
        quit()

    try:
        browser.find_element_by_id('AuthenticationFG.USER_PRINCIPAL').send_keys(identity)
        browser.find_element_by_id('AuthenticationFG.ACCESS_CODE').send_keys(password)

        try:
            browser.find_element_by_id('IMAGECAPTCHA').screenshot('captcha.png')
            cap = recCaptcha('captcha.png')

            while len(cap) > 6 or sum([i not in 'ABCDEFGHKLMNPRTUVWXYabdfhkmnpqrtuwxy2345678' for i in cap]) > 0:
                os.remove("captcha.png")
                browser.find_element_by_id('TEXTIMAGE').click()
                browser.find_element_by_id('IMAGECAPTCHA').screenshot('captcha.png')
                cap = recCaptcha('captcha.png')

            time.sleep(1.2)
            browser.find_element_by_id('IMAGECAPTCHA').screenshot('captchaaa.png')
            cap = recCaptcha('captchaaa.png')
            print(cap)
            browser.find_element_by_id('AuthenticationFG.VERIFICATION_CODE').clear()
            time.sleep(0.5)
            browser.find_element_by_id('AuthenticationFG.VERIFICATION_CODE').send_keys(cap)
            time.sleep(2)
            browser.find_element_by_id('VALIDATE_RM_PLUS_CREDENTIALS_CATCHA_DISABLED').click()
            os.remove("captchaaa.png")
            os.remove("captcha.png")
            browser.implicitly_wait(8)
            # Assign aa, bb just for the sake of password timeline
            aa = browser.find_element_by_id('signOnpwd').get_attribute('innerText')
            bb = browser.find_element_by_id('HREF_DashboardFG.LOGIN_EXPIRY_DAYS').get_attribute('innerText')
            print(
                f"{'Login Successful..!'}\n\n   {Fore.LIGHTRED_EX}{Style.BRIGHT}{aa}------------------ > > > {Fore.LIGHTGREEN_EX}{Style.BRIGHT}{bb}\n\n")
        except:
            try:
                browser.close()
                try:
                    browser = webdriver.Chrome(options=option)
                    browser.get(url)
                except Exception as e:
                    print(ColoredPrint('Internet Problem\n\n --> >' + str(e), Fore.LIGHTRED_EX))
                    time.sleep(10)
                    quit()

                print('Varify "CAPTCHA" Manually...!!!')
                browser.find_element_by_id('AuthenticationFG.USER_PRINCIPAL').send_keys(identity)
                browser.find_element_by_id('AuthenticationFG.ACCESS_CODE').send_keys(password)
                browser.find_element_by_id('IMAGECAPTCHA').screenshot('captcha.png')
                cap = recCaptcha('captcha.png')

                print(ColoredPrint(cap, Fore.LIGHTRED_EX))
                Image.open('captcha.png').show()
                captcha = input('Enter the "CAPTCH" here --> ')
                if len(captcha) < 1:
                    pass
                else:
                    cap = captcha
                print(ColoredPrint(cap, Fore.LIGHTGREEN_EX))
                time.sleep(0.25)
                browser.find_element_by_id('AuthenticationFG.VERIFICATION_CODE').send_keys(cap)
                time.sleep(2)
                browser.find_element_by_id('VALIDATE_RM_PLUS_CREDENTIALS_CATCHA_DISABLED').click()
                os.remove("captcha.png")
                browser.implicitly_wait(12)
                # Assign aa, bb just for the sake of password timeline
                aa = browser.find_element_by_id('signOnpwd').get_attribute('innerText')
                bb = browser.find_element_by_id('HREF_DashboardFG.LOGIN_EXPIRY_DAYS').get_attribute('innerText')
                print(
                    f"{'Login Successful..!'}\n\n   {Fore.LIGHTRED_EX}{Style.BRIGHT}{aa}------------------ > > > {Fore.LIGHTGREEN_EX}{Style.BRIGHT}{bb}\n\n")
            except Exception as e:
                print(ColoredPrint('"Failed" Due to InCorrect CAPTCHA ... !!!', Fore.LIGHTRED_EX))
                quit(e)
    except Exception as e:
        quit(ColoredPrint(f'Internet / Website is BUSY.....!!\n{e}', Fore.LIGHTRED_EX))
        print(e)

    return browser, aa, bb, dtStamp


# ----------------------------------------------------------------------------------------------------------------------

def user():
    """To take User Inputs & Validate Them Instantly"""
    global lots, lot_names, cells, a, b, w8, sh1, verify, inst_verify, verified

    # Excel Path
    wb = openpyxl.load_workbook(r"Portal.xlsx", read_only=True, data_only=True)

    # getting data from frontend and unpacking it
    sht, rows = frontEnd()
    try:
        int(sht)
    except ValueError:
        print(ColoredPrint('--------------->>>    Installment No. Must Be a "NUMBER" !!!', Fore.LIGHTRED_EX))
        messagebox.showerror("Error", f">>>    Installment No. Must Be a 'NUMBER' !!! & NOT --> {sht}")
        w8 = 9
        quit()
    if int(sht) == 1:
        a = 'First'
        sh1 = wb["First"]
    elif int(sht) == 2:
        b = 'Second'
        sh1 = wb["Second"]
    else:
        print(ColoredPrint('Invalid Input', Fore.LIGHTRED_EX))
        messagebox.showerror("Error", f"Invalid Input : {sht}")
        w8 = 9
        quit()

    for items in rows.split():
        try:
            int(items)
        except ValueError:
            print(ColoredPrint('--------------->>>    LOT No. Must Be a "Numeric Value" !!!', Fore.LIGHTRED_EX))
            messagebox.showerror("Error", f">>>    LOT No. Must Be a 'Numeric Value' !!! & NOT --> {items}")
            w8 = 9
            quit()
        if int(items) > 1:
            cell = 'C' + items
            cells.append(cell)
            lots.append(sh1[cell].value)
            lot_name = sh1[f"B{cell[1:]}"].value
            lot_names.append(lot_name)
        else:
            print(ColoredPrint('Try By Entering All Greater Than 1 values', Fore.LIGHTRED_EX))
            messagebox.showerror("Error", "Invalid Input : Try By Entering All 'Greater Than 1' Values")
            w8 = 9
            quit()
    print(f"{Fore.GREEN}{Style.BRIGHT}\tOK...!!")
    lots = [i for i in lots if i]  # To eliminate the :None values
    lot_names = [i for i in lot_names if i]  # To eliminate the :None values
    if len(lot_names) < 1:
        print(ColoredPrint('NO LOTs FOUND ...!!!', Fore.LIGHTRED_EX))
        messagebox.showerror("Error", f"NO LOTs FOUND ...!!!")
        w8 = 9
        quit()

    def verify_amt():
        conn = sqlite3.connect('Portal_Data.sqlite')
        cur = conn.cursor()
        for part in lots:
            xx = part.replace(" ", "")
            xx = xx.split(',')
            q_marks = len(xx) * '?,'
            lookup = cur.execute('SELECT SUM(Denomination) FROM Portal WHERE Account_No in (' + q_marks[:-1] + ')', xx)
            for totality in lookup:
                verify.append('₹' + str(list(totality)[0]))
        cur.close()
        packed = list(zip(lot_names, verify))
        verified = [one for one in packed]
        return print(verified)

    def view_accounts():
        """To View Details of Selected Accounts"""
        global installments_total, inst, acc, w8
        v = 0
        conn = sqlite3.connect('Portal_Data.sqlite')
        cur = conn.cursor()
        for part in lots:
            xx = part.replace(" ", "")
            xx = xx.split(',')
            print(ColoredPrint(f'--------> > "{lot_names[v]}" < <--------', Fore.LIGHTRED_EX))
            zoo = []
            for iii in xx:
                lookup = cur.execute(
                    'SELECT Account_No, Account_Name, Denomination, Next_Installment_Due_Date, Pending_Installment, '
                    'Advance_Installment, Month_Paid_Upto FROM Portal WHERE Account_No in (?)', (iii,))
                for jk in lookup:
                    zoo.append(jk)
            installments_total = []
            reg_sum = 0
            reg_cnt = 0
            for i in zoo:

                if i[6] == 60:
                    print('\t\t' + str(i[:-3]), '===>{' + str(i[6]) + '} Months Paid:', end="------->> >>")
                    print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}  All Months Are PAID : {i[6]}")

                pending = i[4]
                advance = i[5]
                amt = int(i[2])
                account = i[0]

                if pending is not None:
                    print('\t\t' + str(i[:-3]), '===>{' + str(i[6]) + '} Months Paid:', end="------->> >>")
                    print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}  Pending Installments = [{pending}]*")
                    installments_total.append(amt * (int(pending) + 1))
                    inst.append(pending)
                    acc.append(account)
                elif advance is not None:
                    print('\t\t' + str(i[:-3]), '===>{' + str(i[6]) + '} Months Paid:', end="------->> >>")
                    print(f"{Fore.LIGHTBLUE_EX}{Style.BRIGHT}  Advance Installments = [{advance}]*")
                    installments_total.append(amt * int(advance))
                    inst.append(advance)
                    acc.append(account)
                else:
                    print('\t\t' + str(i[:-3]), '===>{' + str(i[6]) + '} Months Paid:', end="------->> >>")
                    print(f'{Fore.GREEN}{Style.BRIGHT}  Regular_Inst')
                    reg_sum += i[2]
                    reg_cnt += 1
                    installments_total.append(amt * 1)

            print(
                f'{Fore.LIGHTRED_EX}\n\t\t{Fore.LIGHTGREEN_EX}@@@@@ ==>> "Total A/c Numbers":        "{len(zoo)} accounts", '
                f'\n\t\t@@@@@ ==>> "Regular Installment" A/c:  "{reg_cnt} accounts" Of total------> > "Rs. {reg_sum}"')
            print(f'{Back.MAGENTA}{Style.BRIGHT}'
                  f'Total Installment SUM of all Pending + Regular + Advance is = Rupees {sum(installments_total):,}/-')
            v += 1
            inst_verify.append('₹' + str(sum(installments_total)))
        return sum(installments_total)

    verify_amt()
    view_accounts()
    instant = list(zip(lot_names, inst_verify))
    check = [ek for ek in instant]
    # **************   Check if SAME account appears in another LOT...!!   **************
    temp_lis = []
    for Lot_name in lot_names:
        if Lot_name[0].upper() == 'A':
            sht = 1
        else:
            sht = 2
        item = int(Lot_name[1:])

        if int(sht) == 1:
            a = 'First'
            sh1 = wb["First"]
        elif int(sht) == 2:
            b = 'Second'
            sh1 = wb["Second"]
        cell = 'C' + str(item)
        temp_lis.append(sh1[cell].value)

    wb.close()

    new = [i.strip() for i in ','.join(temp_lis).split(',')]

    print(f'\n\nAccounts which are Repeated in {lot_names} are:')
    repeats = set([i for i in new if new.count(i) > 1])
    if repeats:
        print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT} Repeated accounts Found: {repeats}")
    else:
        print(f"{Fore.LIGHTGREEN_EX}{Style.BRIGHT}Good....since, NO Repeated accounts were Found here....!!")

    answer = messagebox.askyesno("Question", f"{verified}\n Before Installments.....\n\n** After Installments "
                                             f"Verification : \n'-->{check}'\n\n\nDo you wants to proceed further ? ?")

    if answer:
        w8 = 1
    else:
        w8 = 9
        quit()

    print(ColoredPrint("Let's Go...........  :)   ", Fore.GREEN))
    return w8


# ------------------------------------------------------------------------------------------------------------------------

def update_lot_history():
    """Update Completed LOTs in our DataBase"""
    connn = sqlite3.connect('Portal_Data.sqlite')
    curr = connn.cursor()
    # # cur.execute('CREATE TABLE History(LOT TEXT, Accounts TEXT, Date TEXT)')
    for i in range(len(lot_names)):
        curr.execute('INSERT OR REPLACE INTO History (LOT, Accounts, Date) VALUES (?,?,?)',
                     (lot_names[i], lots[i], dtStamp))
    connn.commit()
    curr.close()
