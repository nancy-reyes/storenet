""" File to generate database information """

# from sqlalchemy import func
from faker import Faker
from model import Employee, Store, Position, District, Category, connect_to_db, db
from server import app
from random import choice

fake = Faker()


def make_districts():
    """ Let's make some districts! """

    print 'Making Districts...'

    # Let's delete the table in case I want to redo this
    District.query.delete()

    district_dict = {'D01': 'Northwest',
                     'D02': 'Southwest',
                     'D03': 'Midwest',
                     'D04': 'Northeast',
                     'D05': 'Southeast',
                     'D99': 'Corporate HQ'}

    for district in district_dict:
        district_id = district
        name = district_dict[district]

        district_obj = District(district_id=district_id, name=name)

        db.session.add(district_obj)

    db.session.commit()


def make_stores():
    """ Make fake stores and load into database. """

    print 'Making Stores...'

    # Since I like to run this file over and over again:
    Store.query.delete()

    for row in open('misc/seed_stores.txt'):
        row = row.rstrip()
        store_id, name, address, city, state, zipcode, phone = row.split('\t')
        store_id = "{:0>3}".format(store_id)
        zipcode = "{:0>5}".format(zipcode)
        district_id = get_random_district()

        # Instantiate a store using Store class in model.py! Woohoo!
        store = Store(store_id=store_id,
                      name=name,
                      address=address,
                      phone=phone,
                      city=city,
                      state=state,
                      zipcode=zipcode,
                      district_id=district_id)

        # Add to db
        db.session.add(store)

    db.session.commit()


def make_positions():  # LOL that's what she said
    """ Positions """

    print 'Making Positions...'

     # Since I like to run this file over and over again:
    Position.query.delete()

    position_dict = {'01-SM': 'Store Manager',
                     '02-AM': 'Assistant Manager',
                     '03-SS': 'Sales Associate',
                     '10-DM': 'District Manager',
                     '99-HQ': 'Corporate Admin'}

    for position in position_dict:
        pos_id = position
        title = position_dict[position]

        position_obj = Position(pos_id=pos_id, title=title)

        db.session.add(position_obj)

    db.session.commit()


def make_emps():
    """ Make fake users and load into database. """

    print 'Making Employees...'

    # Since I like to run this file over and over again:
    Employee.query.delete()

    # QUESTION: Hm, how do I solve for duplicates, though? *scratches head*
    for emp in range(1,301):
        emp_id = "{:0>5}".format(emp)  # emp_id is 5 digits long
        fname = fake.first_name()
        lname = fake.last_name()
        ssn = fake.ssn()
        password = 'jjjj'  # '{}{}'.format((ssn[-4:]), (lname[0]))
        store_id = get_random_store()

        if mgmt_position[store_id] == []:
            pos_id = '03-SS'
        else:
            pos_id = mgmt_position[store_id].pop()

        # Instantiate an employee using class in model.py
        emp = Employee(emp_id=emp_id, fname=fname,
                       lname=lname, ssn=ssn,
                       password=password, store_id=store_id,
                       pos_id=pos_id)

        # Add employee to db
        db.session.add(emp)

    db.session.commit()


def make_categories():
    """ Let's make some categories! """

    print 'Making Categories...'

    # Let's delete the table in case I want to redo this
    Category.query.delete()

    category_dict = {'opr': 'Operations',
                     'mar': 'Marketing',
                     'mds': 'Markdowns',
                     'vix': 'Visual Merchandising',
                     'pro': 'Promotions',
                     'evt': 'Events',
                     'hrp': 'Human Resources/Payroll',
                     'mis': 'Miscellaneous'}

    for category in category_dict:
        cat_id = category
        name = category_dict[category]

        category_obj = Category(cat_id=cat_id, name=name)

        db.session.add(category_obj)

    db.session.commit()


def make_district_managers():
    """ Adds district managers to the employee table. """

    d01 = Employee(emp_id='11111', fname='Nidhi',
                   lname='Sharma', ssn=fake.ssn(),
                   password='f', store_id='999', pos_id='10-DM')

    d02 = Employee(emp_id='22222', fname='Erin',
                   lname='Cusick', ssn=fake.ssn(),
                   password='f', store_id='999', pos_id='10-DM')

    d03 = Employee(emp_id='33333', fname='Anjou',
                   lname='Ahlborn-Kay', ssn=fake.ssn(),
                   password='f', store_id='999', pos_id='10-DM')

    d04 = Employee(emp_id='44444', fname='Courtney',
                   lname='Cohan', ssn=fake.ssn(),
                   password='f', store_id='999', pos_id='10-DM')

    d05 = Employee(emp_id='55555', fname='Kourtney',
                   lname='Young', ssn=fake.ssn(),
                   password='f', store_id='999', pos_id='10-DM')

    db.session.add_all([d01, d02, d03, d04, d05])
    db.session.commit()


def add_nancy():
    """ Adds me & corp to the employee & store tables """

    corp_store = Store(store_id='999',
                       name='Corporate Headquarters',
                       address='400 Valley Drive',
                       city='Brisbane',
                       state='CA',
                       zipcode='94005', phone='(415) 555-1234',
                       district_id='D99')

    nancy = Employee(emp_id='09332', fname='Nancy',
                     lname='Reyes', ssn='123-45-6789',
                     password='f', store_id='999', pos_id='99-HQ')

    db.session.add_all([nancy, corp_store])
    db.session.commit()


##############################################################################
# Helper Functions


def get_random_store():
    """ Helper function to generate a random store. Will be assigned to
    employee in make_emps function. """

    all_stores = Store.query.all()
    random_store = choice(all_stores).store_id

    return random_store


def get_random_district():
    """ Helper function to generate a random district. Will be assigned to
    random store in make_store function. """

    #  Need to exclude Corporate
    all_districts = District.query.filter(db.not_(District.district_id.in_(['D99']))).all()

    random_district = choice(all_districts).district_id

    return random_district


def get_position():
    """ Helper function. Each store needs(1) Store Manager, (2) Assistant
    Managers. Everyone else will be a Sales associate. This function will
    create a list where these positions can be popped from."""

    # Generate a dictionary with store_id and a poppable list with mgmt pos.
    avail_mgmt_positions = {}
    all_stores = Store.query.all()

    for store in all_stores:
        avail_mgmt_positions[store.store_id] = ['01-SM', '02-AM', '02-AM']

    return avail_mgmt_positions


if __name__ == '__main__':
    connect_to_db(app)

    db.create_all()

    make_districts()
    make_stores()
    mgmt_position = get_position()
    make_positions()
    make_emps()
    make_categories()
    add_nancy()
    make_district_managers()
