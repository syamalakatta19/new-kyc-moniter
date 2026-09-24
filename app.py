from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    Response
)

from database import get_connection
from utils.date_utils import convert_date
from utils.kyc_utils import calculate_status

import csv
import io


app = Flask(__name__)

app.secret_key = "kyc_monitor_secret_key"


# ==========================================
# LOGIN CHECK
# ==========================================

def login_required():

    return "admin" in session


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

        connection = None
        cursor = None

        try:

            connection = get_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            query = """
                SELECT *
                FROM admins
                WHERE username = %s
                AND password = %s
            """

            cursor.execute(
                query,
                (
                    username,
                    password
                )
            )

            admin = cursor.fetchone()

            if admin:

                session["admin"] = username

                flash(
                    "Login successful!",
                    "success"
                )

                return redirect(
                    url_for("dashboard")
                )

            else:

                flash(
                    "Invalid username or password.",
                    "danger"
                )

        except Exception as error:

            flash(
                "Login error: " + str(error),
                "danger"
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("login.html")


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/")
def dashboard():

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # Update status automatically

        cursor.execute("""
            UPDATE customers
            SET kyc_status =
                CASE

                    WHEN kyc_expiry_date < CURDATE()
                    THEN 'Expired'

                    WHEN DATEDIFF(
                        kyc_expiry_date,
                        CURDATE()
                    ) <= 30
                    THEN 'Expiring Soon'

                    ELSE 'Valid'

                END
        """)

        connection.commit()


        # Total

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM customers
        """)

        total = cursor.fetchone()["total"]


        # Valid

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM customers
            WHERE kyc_status = 'Valid'
        """)

        valid = cursor.fetchone()["total"]


        # Expiring

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM customers
            WHERE kyc_status = 'Expiring Soon'
        """)

        expiring = cursor.fetchone()["total"]


        # Expired

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM customers
            WHERE kyc_status = 'Expired'
        """)

        expired = cursor.fetchone()["total"]


        # Recent customers

        cursor.execute("""
            SELECT
                c.*,
                b.branch_name
            FROM customers c

            LEFT JOIN branches b
                ON c.branch_id = b.branch_id

            ORDER BY c.customer_id DESC

            LIMIT 5
        """)

        recent_customers = cursor.fetchall()


        return render_template(
            "dashboard.html",
            total=total,
            valid=valid,
            expiring=expiring,
            expired=expired,
            recent_customers=recent_customers
        )

    except Exception as error:

        flash(
            "Dashboard error: " + str(error),
            "danger"
        )

        return render_template(
            "dashboard.html",
            total=0,
            valid=0,
            expiring=0,
            expired=0,
            recent_customers=[]
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# CUSTOMERS
# ==========================================

@app.route("/customers")
def customers():

    if not login_required():

        return redirect(
            url_for("login")
        )

    search = request.args.get(
        "search",
        ""
    ).strip()

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        if search:

            search_value = f"%{search}%"

            cursor.execute("""
                SELECT
                    c.*,
                    b.branch_name
                FROM customers c

                LEFT JOIN branches b
                    ON c.branch_id = b.branch_id

                WHERE
                    c.full_name LIKE %s
                    OR c.customer_number LIKE %s
                    OR c.account_number LIKE %s

                ORDER BY c.customer_id DESC
            """, (
                search_value,
                search_value,
                search_value
            ))

        else:

            cursor.execute("""
                SELECT
                    c.*,
                    b.branch_name
                FROM customers c

                LEFT JOIN branches b
                    ON c.branch_id = b.branch_id

                ORDER BY c.customer_id DESC
            """)

        customer_list = cursor.fetchall()

        return render_template(
            "customers.html",
            customers=customer_list,
            search=search
        )

    except Exception as error:

        flash(
            "Error loading customers: "
            + str(error),
            "danger"
        )

        return render_template(
            "customers.html",
            customers=[],
            search=search
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# ADD CUSTOMER
# ==========================================

@app.route(
    "/add-customer",
    methods=["GET", "POST"]
)
def add_customer():

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT *
            FROM branches
            ORDER BY branch_name
        """)

        branches = cursor.fetchall()


        if request.method == "POST":

            customer_number = request.form.get(
                "customer_number",
                ""
            ).strip()

            full_name = request.form.get(
                "full_name",
                ""
            ).strip()

            dob = convert_date(
                request.form.get(
                    "dob",
                    ""
                )
            )

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            branch_id = request.form.get(
                "branch_id"
            )

            account_type = request.form.get(
                "account_type",
                ""
            ).strip()

            account_number = request.form.get(
                "account_number",
                ""
            ).strip()

            kyc_document = request.form.get(
                "kyc_document",
                ""
            ).strip()

            issue_date = convert_date(
                request.form.get(
                    "kyc_issue_date",
                    ""
                )
            )

            expiry_date = convert_date(
                request.form.get(
                    "kyc_expiry_date",
                    ""
                )
            )


            if not customer_number:

                flash(
                    "Customer number is required.",
                    "danger"
                )

                return render_template(
                    "add_customer.html",
                    branches=branches
                )


            if not full_name:

                flash(
                    "Full name is required.",
                    "danger"
                )

                return render_template(
                    "add_customer.html",
                    branches=branches
                )


            if dob is None:

                flash(
                    "Invalid DOB.",
                    "danger"
                )

                return render_template(
                    "add_customer.html",
                    branches=branches
                )


            if expiry_date is None:

                flash(
                    "Invalid KYC expiry date.",
                    "danger"
                )

                return render_template(
                    "add_customer.html",
                    branches=branches
                )


            status = calculate_status(
                expiry_date
            )


            cursor.execute("""
                INSERT INTO customers
                (
                    customer_number,
                    full_name,
                    dob,
                    phone,
                    email,
                    branch_id,
                    account_type,
                    account_number,
                    kyc_document,
                    kyc_issue_date,
                    kyc_expiry_date,
                    kyc_status
                )

                VALUES
                (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )
            """, (
                customer_number,
                full_name,
                dob,
                phone,
                email,
                branch_id,
                account_type,
                account_number,
                kyc_document,
                issue_date,
                expiry_date,
                status
            ))


            connection.commit()


            flash(
                "Customer added successfully!",
                "success"
            )

            return redirect(
                url_for("customers")
            )


        return render_template(
            "add_customer.html",
            branches=branches
        )

    except Exception as error:

        if connection:
            connection.rollback()

        flash(
            "Error adding customer: "
            + str(error),
            "danger"
        )

        return render_template(
            "add_customer.html",
            branches=branches
            if "branches" in locals()
            else []
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# EDIT CUSTOMER
# ==========================================

@app.route(
    "/edit-customer/<int:customer_id>",
    methods=["GET", "POST"]
)
def edit_customer(customer_id):

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT *
            FROM customers
            WHERE customer_id = %s
        """, (customer_id,))

        customer = cursor.fetchone()


        if not customer:

            flash(
                "Customer not found.",
                "danger"
            )

            return redirect(
                url_for("customers")
            )


        cursor.execute("""
            SELECT *
            FROM branches
            ORDER BY branch_name
        """)

        branches = cursor.fetchall()


        if request.method == "POST":

            full_name = request.form.get(
                "full_name",
                ""
            ).strip()

            dob = convert_date(
                request.form.get(
                    "dob",
                    ""
                )
            )

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            branch_id = request.form.get(
                "branch_id"
            )

            account_type = request.form.get(
                "account_type",
                ""
            ).strip()

            account_number = request.form.get(
                "account_number",
                ""
            ).strip()

            kyc_document = request.form.get(
                "kyc_document",
                ""
            ).strip()

            issue_date = convert_date(
                request.form.get(
                    "kyc_issue_date",
                    ""
                )
            )

            expiry_date = convert_date(
                request.form.get(
                    "kyc_expiry_date",
                    ""
                )
            )


            if dob is None:

                flash(
                    "Invalid DOB.",
                    "danger"
                )

                return render_template(
                    "edit_customer.html",
                    customer=customer,
                    branches=branches
                )


            if expiry_date is None:

                flash(
                    "Invalid expiry date.",
                    "danger"
                )

                return render_template(
                    "edit_customer.html",
                    customer=customer,
                    branches=branches
                )


            status = calculate_status(
                expiry_date
            )


            cursor.execute("""
                UPDATE customers

                SET
                    full_name = %s,
                    dob = %s,
                    phone = %s,
                    email = %s,
                    branch_id = %s,
                    account_type = %s,
                    account_number = %s,
                    kyc_document = %s,
                    kyc_issue_date = %s,
                    kyc_expiry_date = %s,
                    kyc_status = %s

                WHERE customer_id = %s
            """, (
                full_name,
                dob,
                phone,
                email,
                branch_id,
                account_type,
                account_number,
                kyc_document,
                issue_date,
                expiry_date,
                status,
                customer_id
            ))


            connection.commit()


            flash(
                "Customer updated successfully!",
                "success"
            )

            return redirect(
                url_for("customers")
            )


        return render_template(
            "edit_customer.html",
            customer=customer,
            branches=branches
        )

    except Exception as error:

        if connection:
            connection.rollback()

        flash(
            "Update error: " + str(error),
            "danger"
        )

        return redirect(
            url_for("customers")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# DELETE CUSTOMER
# ==========================================

@app.route(
    "/delete-customer/<int:customer_id>"
)
def delete_customer(customer_id):

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM customers
            WHERE customer_id = %s
        """, (customer_id,))

        connection.commit()

        flash(
            "Customer deleted successfully.",
            "success"
        )

    except Exception as error:

        if connection:
            connection.rollback()

        flash(
            "Delete error: " + str(error),
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("customers")
    )


# ==========================================
# JOINT HOLDERS
# ==========================================

@app.route(
    "/joint-holders/<account_number>"
)
def joint_holders(account_number):

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT *
            FROM customers
            WHERE account_number = %s
        """, (account_number,))

        customer = cursor.fetchone()


        if not customer:

            flash(
                "Account not found.",
                "danger"
            )

            return redirect(
                url_for("customers")
            )


        cursor.execute("""
            SELECT *
            FROM joint_account_holders

            WHERE account_number = %s

            ORDER BY holder_id
        """, (account_number,))

        holders = cursor.fetchall()


        return render_template(
            "joint_holders.html",
            customer=customer,
            holders=holders
        )

    except Exception as error:

        flash(
            "Joint holder error: "
            + str(error),
            "danger"
        )

        return redirect(
            url_for("customers")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# ADD JOINT HOLDER
# ==========================================

@app.route(
    "/add-joint-holder/<account_number>",
    methods=["GET", "POST"]
)
def add_joint_holder(account_number):

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT *
            FROM customers
            WHERE account_number = %s
        """, (account_number,))

        customer = cursor.fetchone()


        if not customer:

            flash(
                "Account not found.",
                "danger"
            )

            return redirect(
                url_for("customers")
            )


        if request.method == "POST":

            holder_name = request.form.get(
                "holder_name",
                ""
            ).strip()

            dob = convert_date(
                request.form.get(
                    "dob",
                    ""
                )
            )

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            kyc_document = request.form.get(
                "kyc_document",
                ""
            ).strip()

            issue_date = convert_date(
                request.form.get(
                    "kyc_issue_date",
                    ""
                )
            )

            expiry_date = convert_date(
                request.form.get(
                    "kyc_expiry_date",
                    ""
                )
            )


            if not holder_name:

                flash(
                    "Holder name is required.",
                    "danger"
                )

                return render_template(
                    "add_joint_holder.html",
                    customer=customer
                )


            if expiry_date is None:

                flash(
                    "Invalid KYC expiry date.",
                    "danger"
                )

                return render_template(
                    "add_joint_holder.html",
                    customer=customer
                )


            status = calculate_status(
                expiry_date
            )


            cursor.execute("""
                INSERT INTO joint_account_holders
                (
                    account_number,
                    holder_name,
                    dob,
                    phone,
                    email,
                    kyc_document,
                    kyc_issue_date,
                    kyc_expiry_date,
                    kyc_status
                )

                VALUES
                (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """, (
                account_number,
                holder_name,
                dob,
                phone,
                email,
                kyc_document,
                issue_date,
                expiry_date,
                status
            ))


            connection.commit()


            flash(
                "Joint holder added successfully!",
                "success"
            )

            return redirect(
                url_for(
                    "joint_holders",
                    account_number=account_number
                )
            )


        return render_template(
            "add_joint_holder.html",
            customer=customer
        )

    except Exception as error:

        if connection:
            connection.rollback()

        flash(
            "Error adding holder: "
            + str(error),
            "danger"
        )

        return redirect(
            url_for(
                "joint_holders",
                account_number=account_number
            )
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# SCHEDULE RE-KYC
# ==========================================

@app.route(
    "/schedule/<int:customer_id>",
    methods=["GET", "POST"]
)
def schedule_rekyc(customer_id):

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT *
            FROM customers
            WHERE customer_id = %s
        """, (customer_id,))

        customer = cursor.fetchone()


        if not customer:

            flash(
                "Customer not found.",
                "danger"
            )

            return redirect(
                url_for("customers")
            )


        if request.method == "POST":

            scheduled_date = convert_date(
                request.form.get(
                    "scheduled_date",
                    ""
                )
            )

            remarks = request.form.get(
                "remarks",
                ""
            ).strip()


            if scheduled_date is None:

                flash(
                    "Invalid schedule date.",
                    "danger"
                )

                return render_template(
                    "schedule.html",
                    customer=customer
                )


            cursor.execute("""
                INSERT INTO rekyc_schedule
                (
                    customer_id,
                    scheduled_date,
                    status,
                    remarks
                )

                VALUES
                (
                    %s, %s, 'Pending', %s
                )
            """, (
                customer_id,
                scheduled_date,
                remarks
            ))


            connection.commit()


            flash(
                "Re-KYC scheduled successfully!",
                "success"
            )

            return redirect(
                url_for("customers")
            )


        return render_template(
            "schedule.html",
            customer=customer
        )

    except Exception as error:

        if connection:
            connection.rollback()

        flash(
            "Scheduling error: "
            + str(error),
            "danger"
        )

        return redirect(
            url_for("customers")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# BRANCH REPORT
# ==========================================

@app.route("/reports")
def reports():

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT

                b.branch_code,

                b.branch_name,

                b.city,

                COUNT(c.customer_id)
                    AS pending_count

            FROM branches b

            LEFT JOIN customers c

                ON b.branch_id = c.branch_id

                AND c.kyc_status IN
                (
                    'Expired',
                    'Expiring Soon'
                )

            GROUP BY
                b.branch_id,
                b.branch_code,
                b.branch_name,
                b.city

            ORDER BY b.branch_name
        """)

        report_data = cursor.fetchall()


        return render_template(
            "reports.html",
            reports=report_data
        )

    except Exception as error:

        flash(
            "Report error: " + str(error),
            "danger"
        )

        return render_template(
            "reports.html",
            reports=[]
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# CSV DOWNLOAD
# ==========================================

@app.route("/download-report")
def download_report():

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT

                c.customer_number,

                c.full_name,

                c.account_number,

                b.branch_name,

                c.kyc_document,

                c.kyc_expiry_date,

                c.kyc_status

            FROM customers c

            LEFT JOIN branches b
                ON c.branch_id = b.branch_id

            WHERE c.kyc_status IN
            (
                'Expired',
                'Expiring Soon'
            )

            ORDER BY
                b.branch_name,
                c.full_name
        """)

        data = cursor.fetchall()


        output = io.StringIO()

        writer = csv.writer(output)


        writer.writerow([
            "Customer Number",
            "Customer Name",
            "Account Number",
            "Branch",
            "KYC Document",
            "KYC Expiry Date",
            "KYC Status"
        ])


        for row in data:

            writer.writerow([
                row["customer_number"],
                row["full_name"],
                row["account_number"],
                row["branch_name"],
                row["kyc_document"],
                row["kyc_expiry_date"],
                row["kyc_status"]
            ])


        response = Response(
            output.getvalue(),
            mimetype="text/csv"
        )


        response.headers[
            "Content-Disposition"
        ] = (
            "attachment; "
            "filename=kyc_pending_report.csv"
        )


        return response

    except Exception as error:

        flash(
            "CSV error: " + str(error),
            "danger"
        )

        return redirect(
            url_for("reports")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# START FLASK
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )