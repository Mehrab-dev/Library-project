import sqlite3
import re
import jdatetime
import webbrowser



# ساخت جدول کاربر
conn = sqlite3.Connection("Khane_Tajrobe.sqlite3")
cur = conn.cursor()
cur.execute(""" create table if not exists members(Membership_code integer primary key autoincrement , National_code text , Date_membership text ,
                Gender text , Name text , Lastname text , Mobile1 text , Date_birth text , Mobile2 text , Description text , Loaned_book integer ,
                Borrowed_book integer , Validity integer , Active text) """)
conn.commit()
conn.close()

# ساخت جدول کتاب
conn = sqlite3.Connection("Khane_Tajrobe.sqlite3")
cur = conn.cursor()
cur.execute(""" create table if not exists books(Bcode text , National_code text , Name text ,Lastname text , Title_book  text , Publisher text ,
                Number_page integer , Volume_number integer , Cover_type text , Size text , Description text , Statuse text , Price integer ,
                Depreciation integer , Value integer , Owner_share integer , Page_price integer , Date_registretion text , Active TEXT) """)
conn.commit()
conn.close()

# ساخت جدول امانت کتاب
conn = sqlite3.Connection("Khane_Tajrobe.sqlite3")
cur = conn.cursor()
cur.execute(""" create table if not exists trust(Bcode text , National_code text , Name text , Lastname text , Title text , Publisher text ,
                Owner_name text , Owner_lastname text , Out_description text , Price integer , Date_trust text) """)
conn.commit()
conn.close()

# ساخت جدول بازگشت کتاب
conn = sqlite3.Connection("Khane_Tajrobe.sqlite3")
cur = conn.cursor()
cur.execute(""" create table if not exists return(Bcode text , National_code text , Name text , Lastname text , Title text ,
                Publisher text , Owner_name text , Owner_lastname text , in_description text , Price integer , Value integer ,
                Total_amount integer , Validity integer , Cash integer , Loan_days integer , Payment_method text , Score_out_of_10 integer ,
                Date_return text) """)
conn.commit()
conn.close()


def connection(cmd) :
    try :
        head = []
        conn = sqlite3.Connection("Khane_Tajrobe.sqlite3")
        cur = conn.cursor()
        data = cur.execute(cmd)
        header = data.description
        if header != None :
            for i in header :
                head.append(i[0])
        unpack = cur.fetchall()
        conn.commit()
        return unpack,head
    except sqlite3.DataError as e :
        print(f" : اتصال با دیتابیس برقرار نشد. {e}")
        return None,None
    finally :
        conn.close()

# توابع کاربر
def add_member(national_code,gender,name,lastname,mobile1,date_birth,mobile2=None,description=None):

    today = jdatetime.datetime.now().strftime("%y-%m-%d")
    if not national_code.isdigit():
        return "کد ملی فقط باید شامل عدد باشد."
    if not re.fullmatch(r"\d{10}", national_code) :
        return "کد ملی باید فقط 10 رقم باشد. مجدد کد ملی را وارد کنید."
    cmd = f"""SELECT * FROM members WHERE National_code='{national_code}'"""
    exists,_ = connection(cmd)
    if exists:
        return "کد ملی قبلاً ثبت شده و تکراری است."

    if not mobile1.isdigit() :
        return "برای شماره موبایل اصلی فقط از عدد استفاده کنید."
    if not re.fullmatch(r"09\d{9}",mobile1) :
        return "شماره موبایل اصلی باید 11 رقم باشد.مجدد وارد کنید."
    cmd = f""" select * from members where Mobile1='{mobile1}' """
    mobile1_exists,_ = connection(cmd)
    if mobile1_exists :
        return "شماره موبایل قبلا ثبت شده است."

    if mobile2 :
        if not mobile2.isdigit() :
            return "برای شماره موبایل فرعی فقط از عدد استفاده کنید."
        if not re.fullmatch(r"09\d{9}",mobile2) :
            return "شماره موبایل فرعی باید 11 رقم باشد.مجدد وارد کنید."
        cmd = f""" select * from members where Mobile2='{mobile2}' """
        mobile2_exists,_ = connection(cmd)
        if mobile2_exists :
            return "شماره موبایل قبلا ثبت شده است."

    validity = 0
    loaned_book = 0
    borrowed_book = 0
    active = 'فعال'
    mobile2_value = f" '{mobile2}' " if mobile2 else "NULL"

    cmd = f""" insert into members(National_code,Date_membership,Gender,Name,Lastname,Mobile1,Date_birth,Mobile2,Description,Loaned_book,
                Borrowed_book,Validity,Active) values ('{national_code}','{today}','{gender}','{name}','{lastname}','{mobile1}','{date_birth}',
                {mobile2_value},'{description}',{loaned_book},{borrowed_book},{validity},'{active}') """
    try :
        connection(cmd)
        return "کاربر با موفقیت اضافه شد."
    except Exception as e :
        return f" : ارتباط با دیتابیس با مشکل مواجه شد{e}"
def deactive_member_by_membership(membership) :
    membership = str(membership)
    if not membership.isdigit() :
        return "کد عضویت نامعتبر است."
    cmd = f"select * from members where Membership_code = {membership}"
    exists , _ = connection(cmd)
    if not exists :
        return "کاربری با این کد عضویت موجود نیست."
    carrent_status = exists[0][-1]
    if carrent_status == "غیرفعال" :
        return "کاربر قبلا غیرفعال شده است."
    cmd = f"update members set Active = 'غیرفعال' where Membership_code = {membership} "
    connection(cmd)
    return "کاربر غیرفعال شد."

def search_member_by_mobile (mobile) :
    if not re.fullmatch(r"09\d{9}",mobile) :
        return "شماره موبایل نامعتبر است."
    cmd = f""" select Membership_code as 'کد عضویت',National_code as 'کد ملی',Date_membership as 'تاریخ عضویت',"
               "Gender as 'جنسیت',Name as 'نام',Lastname as 'نام خانوادگی',Mobile1 as 'شماره موبایل اصلی',Date_birth as 'تاریخ عضویت',"
               "Mobile2 as 'شماره موبایل فرعی',Description as 'توضیحات',Loaned_book as 'تعداد کتاب امانت داده',"
               "Borrowed_book as 'تعداد کتاب امانت گرفته',Validity as 'اعتبار',Active as 'وضعیت کاربر' from members where Mobile1 = '{mobile}' or Mobile2 = '{mobile}' """
    unpack , head = connection(cmd)
    if not unpack :
        return "موردی یافت نشد."
def search_member_by_national_code (national_code) :
    if not re.fullmatch(r"\d{10}",national_code) or not national_code.isdigit() :
        return "کد ملی نامعتبر است."
    cmd = f""" select Membership_code as 'کد عضویت',National_code as 'کد ملی',Date_membership as 'تاریخ عضویت',"
               "Gender as 'جنسیت',Name as 'نام',Lastname as 'نام خانوادگی',Mobile1 as 'شماره موبایل اصلی',Date_birth as 'تاریخ عضویت',"
               "Mobile2 as 'شماره موبایل فرعی',Description as 'توضیحات',Loaned_book as 'تعداد کتاب امانت داده',"
               "Borrowed_book as 'تعداد کتاب امانت گرفته',Validity as 'اعتبار',Active as 'وضعیت کاربر' from members where National_code = '{national_code}' """
    unpack , head = connection(cmd)
    if not unpack :
        return "موردی یافت نشد."
def search_member_by_membership_code (membership_code) :
    if not membership_code.isdigit() :
        return "کد عضویت نامعتبر است."
    cmd = f""" select Membership_code as 'کد عضویت',National_code as 'کد ملی',Date_membership as 'تاریخ عضویت',"
               "Gender as 'جنسیت',Name as 'نام',Lastname as 'نام خانوادگی',Mobile1 as 'شماره موبایل اصلی',Date_birth as 'تاریخ عضویت',"
               "Mobile2 as 'شماره موبایل فرعی',Description as 'توضیحات',Loaned_book as 'تعداد کتاب امانت داده',"
               "Borrowed_book as 'تعداد کتاب امانت گرفته',Validity as 'اعتبار',Active as 'وضعیت کاربر' from members where Membership_code = {membership_code} """
    unpack , head = connection(cmd)
    if not unpack :
        return "موردی یافت نشد."
def search(method,value) :
    if method == "کد ملی" :
        return search_member_by_national_code(value)
    if method == "کد عضویت" :
        return search_member_by_membership_code(value)
    if method == "شماره موبایل" :
        return search_member_by_mobile(value)
    else :
        return "روش جستجو نامعتبر است."

def update_member (membership_code,national_code=None,gender=None,name=None,lastname=None,mobile1=None,birth_date=None,mobile2=None,description=None) :
    erorr = {}
    if not membership_code.isdigit() :
        erorr["Membership_code"] = "کد عضویت نامعتبر است."
        return {"erorr" : erorr}
    cmd = f""" select * from members where Membership_code = {membership_code} """
    exists , _ = connection(cmd)
    if not exists :
        erorr["Membership_code"] = "هیچ کاربری با این کد عضویت ثبت نشده است."
        return {"erorr" : erorr}
    exists = exists[0]

    national_code = national_code if national_code else exists[1]
    if not re.fullmatch(r"\d{10}",national_code) :
        erorr["National_code"] = "کد ملی اشتباه است . مجدد وارد کنید."

    gender = gender or exists[3]
    name = name or exists[4]
    lastname = lastname or exists[5]

    mobile1 = mobile1 if mobile1 else exists[6]
    if not re.fullmatch(r"09\d{9}",mobile1) :
        erorr["Mobile1"] = "شماره موبایل اشتباه است."
    birth_date = birth_date or exists[7]

    mobile2 = mobile2 if mobile2 else exists[8]
    if mobile2 and not re.fullmatch(r"09\d{9}",mobile2) :
        erorr["Mobile2"] = "شماره موبایل فرعی نامعتبر است."

    description = description or exists[9]
    if erorr :
        return {"error": erorr}

    cmd = f""" update members set National_code='{national_code}',Gender='{gender}',Name='{name}',Lastname='{lastname}',Mobile1='{mobile1}',
               Date_birth='{birth_date}',Mobile2='{mobile2}',Description='{description}' where Membership_code={membership_code} """
    try :
        connection(cmd)
        return "اطلاعات کاربر با موفقیت بروزرسانی شد."
    except Exception as e :
        return f" : خطا در اتصال به دیتابیس{e}"

def select_all_member() :
    try :
        cmd = ("select Membership_code as 'کد عضویت',National_code as 'کد ملی',Date_membership as 'تاریخ عضویت',"
               "Gender as 'جنسیت',Name as 'نام',Lastname as 'نام خانوادگی',Mobile1 as 'شماره موبایل اصلی',Date_birth as 'تاریخ عضویت',"
               "Mobile2 as 'شماره موبایل فرعی',Description as 'توضیحات',Loaned_book as 'تعداد کتاب امانت داده',"
               "Borrowed_book as 'تعداد کتاب امانت گرفته',Validity as 'اعتبار',Active as  'وضعیت کاربر' from members")
        result,header = connection(cmd)
        if result is None :
            return "خطا در دریافت اطلاعات کاربران"
            return None
        return result,header
    except Exception as e :
        return f" : خطا در اتصال به دیتابیس{e}"
        return None

# توابع کتاب ها
def add_book(dewey,membership_code,title,publisher,number_page,volume_number,price,depreciation,cover_type=None,size=None,description=None) :
    today = jdatetime.date.today().strftime("%y-%m-%d")
    if not dewey.isdigit() :
        return "کد دیویی کتاب باید فقط شامل عدد باشد."


    if not membership_code.isdigit() :
        return "کد عضویت باید فقط شامل عدد باشد."
    cmd = f""" select National_code,Name,Lastname from members where Membership_code='{membership_code}' """
    exists,_ = connection(cmd)
    if not exists :
        return "کد عضویت وارد شده موجود نیست.مجدد وارد کنید."
    national_code,name,lastname = exists[0]
    cmd = f""" select count(*) from books where Bcode like '{dewey}/%/{membership_code}' """
    result,_ = connection(cmd)
    book_count = (int(result[0][0]) if result and result[0][0] is not None else 0) + 1
    bcode = f"{dewey}/{book_count}/{membership_code}"

    if not number_page.isdigit() :
        return "برای تعداد صفحه فقط از عدد استفاده کنید."
    number_page = int(number_page)

    if not volume_number.isdigit() :
        return "برای شماره جلد فقط از عدد استفاده کنید."
    volume_number = int(volume_number)

    if not depreciation.isdigit() or int(depreciation) >= 100 :
        return "برای استهلاک کتاب فقط از عدد و عدد کوچک تر از 100 استفاده کنید."
    depreciation = int(depreciation)
    price = int(price)
    value = price - (price * (depreciation/100))
    owner_share = value * 0.05
    price_page = int(value/number_page)
    statuse = "موجود"
    active = "فعال"

    cmd = f"SELECT Active FROM members WHERE National_code='{national_code}'"
    member_status_result, _ = connection(cmd)
    if member_status_result:
        member_status = member_status_result[0][0]
        if member_status == "غیرفعال":
            return "این کاربر غیرفعال است و نمی‌تواند کتابی به کتابخانه اضافه کند."

    cmd = f""" insert into books(Bcode,National_code,Name,Lastname,Title_book,Publisher,Number_page,Volume_number,Cover_type,Size,
               Description,Statuse,Price,Depreciation,Value,Owner_share,Page_price,Date_registretion,Active) values ('{bcode}','{national_code}',
               '{name}','{lastname}','{title}','{publisher}',{number_page},{volume_number},'{cover_type}','{size}',
               '{description}','{statuse}',{price},{depreciation},{value},{owner_share},{price_page},'{today}','{active}') """
    try :
        connection(cmd)
        cmd = f""" update members set Loaned_book = Loaned_book + 1 where National_code = '{national_code}' """
        connection(cmd)

        cmd = f""" update members set Validity = Validity + {owner_share} where Membership_code='{membership_code}' """
        connection(cmd)
        return "کتاب با موفقیت در دیتابیس ثبت شد."
    except Exception as e :
        return f" : خطا در اتصال به دیتابیس{e}"

def search_book_by_bcode (bcode) :
    cmd = f""" select Bcode as 'کد کتاب',National_code as 'کد ملی',Name as 'نام مالک',Lastname as 'نام خانوادگی مالک',"
               "Title_book as 'عنوان کتاب',Publisher as 'ناشر',Number_page as 'تعداد صفحه',Volume_number as 'شماره جلد',"
               "Cover_type as 'نوع جلد',Size as 'قطع',Description as 'توضیحات',Statuse as 'وضعیت',price as 'قیمت',"
               "Depreciation as 'درصد استهلاک',Value as 'قیمت نهایی کتاب',Owner_share as 'سهم مالک',Page_price as 'قیمت صفحه',"
               "Date_registretion as 'تاریخ ثبت',Active as 'فعال-غیرفعال' from books where Bcode = '{bcode}' """
    unpack , head = connection(cmd)
    if not unpack :
        return "کد کتاب نامعتبر است."
def search_book_by_national_code (national_code) :
    if not re.fullmatch(r"\d{10}",national_code) or not national_code.isdigit() :
        return "کد ملی نامعتبر است."
    cmd = f""" select Bcode as 'کد کتاب',National_code as 'کد ملی',Name as 'نام مالک',Lastname as 'نام خانوادگی مالک',"
               "Title_book as 'عنوان کتاب',Publisher as 'ناشر',Number_page as 'تعداد صفحه',Volume_number as 'شماره جلد',"
               "Cover_type as 'نوع جلد',Size as 'قطع',Description as 'توضیحات',Statuse as 'وضعیت',price as 'قیمت',"
               "Depreciation as 'درصد استهلاک',Value as 'قیمت نهایی کتاب',Owner_share as 'سهم مالک',Page_price as 'قیمت صفحه',"
               "Date_registretion as 'تاریخ ثبت',Active as 'فعال-غیرفعال' from books where National_code = '{national_code}' """
    unpack , head = connection(cmd)
    if not unpack :
        return "کد ملی موجود نیست."
def search(method,value) :
    if method == "کد کتاب" :
        return search_book_by_bcode(value)
    if method == "کد ملی" :
        return search_book_by_national_code(value)
    else :
        return "روش جستجو نامعتبر است."

def deactivate_book(bcode):
    if not bcode:
        return "کد کتاب نمیتواند خالی باشد."

    cmd = f"SELECT Active FROM books WHERE Bcode='{bcode}'"
    exists, _ = connection(cmd)
    if not exists:
        return "کتابی با این کد وجود ندارد."
    current_status = exists[0][0]

    if current_status == "غیرفعال":
        return "این کتاب قبلا غیرفعال شده است."

    cmd = f"UPDATE books SET Active = 'غیرفعال' WHERE Bcode='{bcode}'"
    connection(cmd)
    return "کتاب با موفقیت غیرفعال شد."

def update_books (bcode,title=None,publisher=None,number_page=None,volume_number=None,cover_type=None,size=None,description=None,price=None,depreciation=None,) :
    error = {}
    if not bcode :
        error["Bcode"] = "کد کتاب نمیتواند خالی باشد."
        return {"error" : error}
    cmd = f""" select Title_book,Publisher,Number_page,Volume_number,Cover_type,Size,Description,Price,Depreciation from books 
               where Bcode = '{bcode}' """
    exists , _ = connection(cmd)
    if not exists :
        error["Bcode"] = "کتابی با این کد ثبت نشده است."
        return {"error" : error}
    old_title,old_Publisher,old_Number_page,old_Volume_number,old_Cover_type,old_Size,old_Description,old_Price,old_Depreciation = exists[0]

    title = title or old_title
    publisher = publisher or old_Publisher
    number_page = number_page if number_page else str(old_Number_page)
    if not number_page.isdigit() :
        error["Number_page"] = "شماره صفحه فقط باید عدد باشد."
    volume_number = volume_number if volume_number else str(old_Volume_number)
    if not volume_number.isdigit() :
        error["Volume_number"] = "شماره جلد نامعتبر است."

    cover_type = cover_type or old_Cover_type
    size = size or old_Size
    description = description or old_Description

    if price is None :
        price = old_Price
    else :
        try :
            price = int(price)
        except :
            error["Price"] = "برای قیمت فقط از عدد استفاده کنید."
    if depreciation is None :
        depreciation = old_Depreciation
    else :
        try :
            depreciation = int(depreciation)
        except :
            error["Depreciation"] = "برای مقدار استهلاک فقط از عدد استفاده کنید."

    if error :
        return {"error" : error}

    value = price - (price * (depreciation /100))
    page_price = int(number_page) / value if (number_page) else 0

    today = jdatetime.date.today().strftime("%y-%m-%d")

    cmd = f""" update books set Title_book='{title}',Publisher='{publisher}',Number_page={number_page},Volume_number={volume_number},
               Cover_type='{cover_type}',Size='{size}',Description='{description}',Price={price},Depreciation={depreciation},Value={value},
               Page_price={page_price} WHERE Bcode='{bcode}' """
    try :
        connection(cmd)
        return "بروزرسانی با موفقیا انجام شد."
    except Exception as e :
        return f" : |خطا در بروزرسانی کتاب{e}"

def select_all_book() :
    try :
        cmd = ("select Bcode as 'کد کتاب',National_code as 'کد ملی',Name as 'نام مالک',Lastname as 'نام خانوادگی مالک',"
               "Title_book as 'عنوان کتاب',Publisher as 'ناشر',Number_page as 'تعداد صفحه',Volume_number as 'شماره جلد',"
               "Cover_type as 'نوع جلد',Size as 'قطع',Description as 'توضیحات',Statuse as 'وضعیت',price as 'قیمت',"
               "Depreciation as 'درصد استهلاک',Value as 'قیمت نهایی کتاب',Owner_share as 'سهم مالک',Page_price as 'قیمت صفحه',"
               "Date_registretion as 'تاریخ ثبت',Active as 'فعال-غیرفعال' from books")
        result,header = connection(cmd)
        if result is None :
            return "خطا در دریافت اطلاعات کتاب"
            return None
        return result,header
    except Exception as e :
        return f" : خطا در اتصال به دیتابیس{e}"
        return None

# توابع مربوط به امانت کتاب
def add_trust(bcode,national_code,price,out_description=None) :
    try :
        if not bcode :
            return "کد کتاب نمیتواند خالی باشد."
        cmd = f""" select Title_book,Publisher,Name,Lastname from books where Bcode='{bcode}' """
        exists,_ = connection(cmd)
        if not exists :
            return "کتابی با این کد موجود نیست"
        title,publisher,owner_name,owner_lastname = exists[0]

        cmd = f"SELECT Active FROM members WHERE National_code='{national_code}'"
        member_status_result , _ = connection(cmd)
        if member_status_result:
            member_status = member_status_result[0][0]
            if member_status == "غیرفعال":
                return "این کاربر غیرفعال است و نمی‌تواند کتابی امانت بگیرد."

        cmd = f"SELECT Statuse FROM books WHERE Bcode='{bcode}'"
        book_status_result, _ = connection(cmd)
        if book_status_result:
            book_status = book_status_result[0][0]
            if book_status == "امانت":
                return "این کتاب در حال حاضر قابل امانت نیست."


        cmd = f"SELECT Active FROM books WHERE Bcode='{bcode}'"
        book_status_result, _ = connection(cmd)
        if book_status_result:
            book_status = book_status_result[0][0]
            if book_status == "غیرفعال":
                return "این کتاب غیرفعال است و نمی‌تواند امانت داده شود."

        if not national_code.isdigit() or not re.fullmatch(r"\d{10}",national_code) :
            return "کدملی اشتباه است."
        cmd = f""" select Name,Lastname from members where National_code='{national_code}' """
        exists,_ = connection(cmd)
        if not exists :
            return "شخصی با این کد ملی ثبت نشده است."
        name,lastname = exists[0]

        today = jdatetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")

        cmd = f""" insert into trust (Bcode,National_code,Name,Lastname,Title,Publisher,Owner_name,Owner_lastname,Out_description,Price,Date_trust)
                   values ('{bcode}','{national_code}','{name}','{lastname}','{title}','{publisher}','{owner_name}','{owner_lastname}',
                   '{out_description}',{price},'{today}') """
        connection(cmd)
        cmd = f""" update books set Statuse = 'امانت' where Bcode = '{bcode}' """
        connection(cmd)
        cmd = f""" update members set Borrowed_book = Borrowed_book +1 where National_code = '{national_code}' """
        connection(cmd)
        return "امانت با موفقیت ثبت شد."
    except Exception as e :
        return f" : خطا در اتصال به دیتابیس{e}"

def delete_trust (bcode) :
    cmd = f""" select National_code,Date_trust from trust where Bcode = '{bcode}' ORDER BY Date_trust DESC LIMIT 1 """
    exists , _ = connection(cmd)
    if not exists :
        return "کتاب با این کد در جدول امانت ثبت نشده است."
    national_code,date_trust = exists[0]

    trust_time = jdatetime.datetime.strptime(date_trust, "%y-%m-%d %H:%M:%S")
    now = jdatetime.datetime.now()
    time_diff = (now - trust_time).total_seconds() / 3600
    if time_diff > 12 :
        return "تایم امانت بیشتر از 12 ساعت است."

    cmd = f""" delete from trust where Bcode = '{bcode}' and National_code = '{national_code}' and Date_trust = '{date_trust}' """
    try :
        connection(cmd)

        cmd = f""" update books set Statuse = 'موجود' where Bcode = '{bcode}' """
        connection(cmd)

        cmd = f""" update members set Borrowed_book = Borrowed_book -1 where National_code = '{national_code}' """
        connection(cmd)
        return f"امانت کتاب با کد{bcode} لغو شد."
    except Exception as e :
        return f" : خطا در اتصال بع دیتابیس{e}"

def search_trust_by_bcode (bcode) :
    cmd = f""" select Bcode as 'کد کتاب',National_code as 'کد ملی امانت گیرنده',Name as 'نام امانت گیرنده',"
               "Lastname as 'نام خانوادگی امانت گیرنده',Title as 'عنوان کتاب',Publisher as 'ناشر',Owner_name as 'نام مالک',"
               "Owner_lastname as 'نام خانوادگی مالک',Out_description as 'توضیحات',Price as 'قیمت هنگام امانت',"
               "Date_trust as 'تاریخ ثبت' from trust where Bcode = '{bcode}' """
    unpack , head = connection(cmd)
    if not unpack :
        return "امانتی با این کد ثبت نشده است."
def search_trust_by_national_code (national_code) :
    if not re.fullmatch(r"\d{10}",national_code) or not national_code.isdigit() :
        return "کد ملی نامعتبر است."
    cmd = f""" select Bcode as 'کد کتاب',National_code as 'کد ملی امانت گیرنده',Name as 'نام امانت گیرنده',"
               "Lastname as 'نام خانوادگی امانت گیرنده',Title as 'عنوان کتاب',Publisher as 'ناشر',Owner_name as 'نام مالک',"
               "Owner_lastname as 'نام خانوادگی مالک',Out_description as 'توضیحات',Price as 'قیمت هنگام امانت',"
               "Date_trust as 'تاریخ ثبت' from trust where National_code = '{national_code}' """
    unpack , head = connection(cmd)
    if not unpack :
        return "هیچ کتابی در امانت ها با این کد ملی ثبت نشده است."
def search(method,value) :
    if method == "کدکتاب" :
        return search_trust_by_bcode(value)
    if method == "کد ملی" :
        return search_trust_by_national_code(value)
    else :
        return "روش جستجو نامعتبر است."

def select_all_trust() :
    try :
        cmd = ("select Bcode as 'کد کتاب',National_code as 'کد ملی امانت گیرنده',Name as 'نام امانت گیرنده',"
               "Lastname as 'نام خانوادگی امانت گیرنده',Title as 'عنوان کتاب',Publisher as 'ناشر',Owner_name as 'نام مالک',"
               "Owner_lastname as 'نام خانوادگی مالک',Out_description as 'توضیحات',Price as 'قیمت هنگام امانت',"
               "Date_trust as 'تاریخ ثبت' from trust ")
        result,header = connection(cmd)
        if result is None :
            return "هیچ امانتی در جدول ثبت نشده است"
            return None
        return result,header
    except Exception as  e :
        return f" : خطا در اتصال به دیتابیس{e}"


# توابع مربوط به بازگشت کتاب
def add_return(bcode,national_code,price,payment_method,score,description=None) :
    try :
        cmd = f""" select Title_book,Publisher,Name,Lastname,Depreciation from books where Bcode = '{bcode}' """
        exists_bcode,_ = connection(cmd)
        if not exists_bcode :
            return "کتابی با این کد در کتابخانه ثبت نشده است"
        title,publisher,owner_name,owner_lastname,depreciation = exists_bcode[0]

        cmd = f""" select Statuse from books where Bcode = '{bcode}' """
        status_book,_ = connection(cmd)
        current_status = status_book[0][0]
        if current_status == "موجود" :
            return "بازگشت کتاب قبلا ثبت شده است"

        if not national_code.isdigit() or not re.fullmatch(r"\d{10}",national_code) :
            return "کد ملی نامعتبر است"
        cmd = f""" select Name,Lastname from members where National_code = '{national_code}' """
        exists , _ = connection(cmd)
        if not exists :
            return "کاربری با این کد ملی ثبت نشده است"
        name,lastname = exists[0]

        depreciation = int(depreciation)
        value = price - (price * (depreciation/100))

        cmd = f""" select Date_trust from trust where Bcode = '{bcode}' order by Date_trust desc limit 1 """
        last_trust_date_result, _ = connection(cmd)
        if not last_trust_date_result:
            return "اطلاعات امانت قبلی برای این کتاب وجود ندارد"

        last_trust_date_str = last_trust_date_result[0][0]
        last_trust_date = jdatetime.datetime.strptime(last_trust_date_str, "%y-%m-%d %H:%M:%S").date()
        today = jdatetime.date.today()
        loan_days = (today - last_trust_date).days

        total_amount = value * loan_days * 0.05

        cmd = f""" select Validity from members where National_code = '{national_code}' """
        validity_result, _ = connection(cmd)
        validity = validity_result[0][0] if validity_result else 0

        remaining_validity = max(validity - total_amount, 0)
        if total_amount == 0 :
            cash = 0
        elif validity >= total_amount :
            cash = 0
        elif total_amount > validity :
            cash = total_amount - validity

        today_shamsi = jdatetime.date.today().strftime("%y-%m-%d")

        cmd = f""" insert into return (Bcode,National_code,Name,Lastname,Title,Publisher,Owner_name,Owner_lastname,in_description,Price,
                  Value,Total_amount,Validity,Cash,Loan_days,Payment_method,Score_out_of_10,Date_return) values ('{bcode}','{national_code}','{name}',
                  '{lastname}','{title}','{publisher}','{owner_name}','{owner_lastname}','{description}',{price},{value},{total_amount},{validity},
                  {cash},{loan_days},'{payment_method}',{score},'{today_shamsi}')"""
        connection(cmd)
        cmd = f""" update members set Validity = {remaining_validity} where National_code = '{national_code}' """
        connection(cmd)
        cmd = f""" update books set Statuse = 'موجود' where Bcode = '{bcode}' """
        connection(cmd)

        return "کتاب با موفقیت در جدول بازگشت ها ثبت شد"
    except Exception as e :
        return f" : خطا در اتصال به دیتابیس{e}"

def search_return_by_bcode (bcode) :
    try :
        cmd = f""" select Bcode as 'کد کتاب',National_code as 'کد ملی امانت گیرنده',Name as 'نام امانت گیرنده',"
                   "Lastname as 'نام خانوادگی امانت گیرنده',Title as 'عنوان کتاب',Publisher as 'ناشر',Owner_name as 'نام مالک',"
                   "Owner_lastname as 'نام خانوادگی مالک',in_description as 'توضیحات',Price as 'قیمت',Value as 'ارزش نهایی',"
                   "Total_amount as 'مبلغ نهایی پرداختی',Validity as 'اعتبار',Loan_days as 'مدت روز امانت',Payment_method as 'شیوه پرداخت',"
                   "Score_out_of_10 as 'امتیاز کاربر',Date_return as 'تاریخ ثبت' from return where Bcode = '{bcode}' """
        unpack , head = connection(cmd)
        if not unpack :
            return "کتاب با این کد در جدول بازگشت ثبت نشده است."
    except Exception as e :
        return f" : خطایی رخ داد{e}"
def search_return_by_national_code (national_code) :
    try :
        if not re.fullmatch(r"\d{10}",national_code) or not national_code.isdigit() :
            return "کد ملی نادرست است."
        cmd = f""" select Bcode as 'کد کتاب',National_code as 'کد ملی امانت گیرنده',Name as 'نام امانت گیرنده',"
                   "Lastname as 'نام خانوادگی امانت گیرنده',Title as 'عنوان کتاب',Publisher as 'ناشر',Owner_name as 'نام مالک',"
                   "Owner_lastname as 'نام خانوادگی مالک',in_description as 'توضیحات',Price as 'قیمت',Value as 'ارزش نهایی',"
                   "Total_amount as 'مبلغ نهایی پرداختی',Validity as 'اعتبار',Loan_days as 'مدت روز امانت',Payment_method as 'شیوه پرداخت',"
                   "Score_out_of_10 as 'امتیاز کاربر',Date_return as 'تاریخ ثبت' from return where National_code = '{national_code}' """
        unpack , head = connection(cmd)
        if not unpack :
            return "کتاب با این کد قسمت بازگشت ها  ثبت نشده است."
    except Exception as e :
        return f" : خطایی رخ داد{e}"
def search (method,value) :
    if method ==  "کدکتاب" :
        return search_return_by_bcode(value)
    if method == "کد ملی" :
        return search_return_by_national_code(value)
    else :
        return "روش جستجو نامعتبر است."

def select_all_return() :
    try :
        cmd = ("select Bcode as 'کد کتاب',National_code as 'کد ملی امانت گیرنده',Name as 'نام امانت گیرنده',"
               "Lastname as 'نام خانوادگی امانت گیرنده',Title as 'عنوان کتاب',Publisher as 'ناشر',Owner_name as 'نام مالک',"
               " Owner_lastname as 'نام خانوادگی مالک',in_description as 'توضیحات',Price as 'قیمت',Value as 'ارزش نهایی',"
               "Total_amount as 'مبلغ نهایی پرداختی',Validity as 'اعتبار',Cash as 'ودیعه نقدی دریافت شده',Loan_days as 'مدت روز امانت',"
               "Payment_method as 'شیوه پرداخت',Score_out_of_10 as 'امتیاز کاربر',Date_return as 'تاریخ ثبت' from return ")
        result,header = connection(cmd)
        if result is None :
            return "هیچ بازگشت کتابی ثبت نشده است"
            return None
        return result,header
    except Exception as e :
        return f" : خطا در اتصال به دیتابیس{e}"



def open_iranketab():
    chrome_path = '"C:/Program Files/Google/Chrome/Application/chrome.exe" %s'
    webbrowser.get(chrome_path).open("https://www.iranketab.ir/")
