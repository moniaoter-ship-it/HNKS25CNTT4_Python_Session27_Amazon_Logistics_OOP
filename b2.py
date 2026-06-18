from abc import ABC, abstractmethod


class BaseAccount(ABC):
    bank_name = "Vietcombank"

    def __init__(self, account_number, owner_name, balance=0):
        self.account_number = account_number
        self.owner_name = " ".join(owner_name.upper().split())
        self._BaseAccount__balance = balance

    @property
    def balance(self):
        return self.__balance

    def increase(self, amount):
        self.__balance += amount

    def decrease(self, amount):
        self.__balance -= amount

    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

    def __add__(self, other):
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance + other.balance

    def __lt__(self, other):
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance < other.balance

    @staticmethod
    def validate_account_number(account_number):
        return account_number.isdigit() and len(account_number) == 10

    @classmethod
    def update_bank_name(cls, new_name):
        cls.bank_name = new_name


class SavingsAccount(BaseAccount):

    def __init__(self, account_number, owner_name, balance, interest_rate):
        super().__init__(account_number, owner_name, balance)
        self.interest_rate = interest_rate

    def deposit(self, amount):
        self.increase(amount)

    def withdraw(self, amount):
        fee = amount * 0.02

        if amount + fee > self.balance:
            print("Không đủ số dư")
            return

        self.decrease(amount + fee)

    def apply_interest(self):
        interest = self.balance * self.interest_rate
        self.increase(interest)
        return interest


class CreditAccount(BaseAccount):

    def __init__(self, account_number, owner_name, balance, credit_limit):
        super().__init__(account_number, owner_name, balance)
        self.credit_limit = credit_limit

    def deposit(self, amount):
        self.increase(amount)

    def withdraw(self, amount):

        if self.balance - amount < -self.credit_limit:
            print("Vượt quá hạn mức thấu chi")
            return

        self.decrease(amount)


class DigitalPremiumMixin:

    def cashback_reward(self, amount):

        if amount > 5000000:
            return amount * 0.01

        return 0


class HybridAccount(
    SavingsAccount,
    DigitalPremiumMixin
):
    pass


class VNPayGateway:

    def execute_pay(self, account, amount):
        account.withdraw(amount)
        print("Thanh toán qua VNPay thành công")


class ViettelMoneyGateway:

    def execute_pay(self, account, amount):
        account.withdraw(amount)
        print("Thanh toán qua Viettel Money thành công")


def process_payment(gateway, account, amount):

    try:
        gateway.execute_pay(account, amount)

    except AttributeError:
        print("Cổng thanh toán không hợp lệ")


accounts = []
current_account = None

while True:

    print("\n===== VIETCOMBANK DIGIBANK =====")
    print("1. Mở tài khoản")
    print("2. Xem thông tin")
    print("3. Nạp / Rút tiền")
    print("4. Tính lãi")
    print("5. So sánh & Gộp")
    print("6. Thanh toán")
    print("7. Thoát")

    choice = input("Chọn: ")

    if choice == "1":

        print("1. Savings")
        print("2. Credit")
        print("3. Hybrid")

        account_type = input("Loại tài khoản: ")

        account_number = input("Số tài khoản: ")

        if not BaseAccount.validate_account_number(account_number):
            print("Số tài khoản không hợp lệ")
            continue

        owner_name = input("Tên chủ tài khoản: ")

        if account_type == "1":

            rate = float(input("Lãi suất: "))

            current_account = SavingsAccount(
                account_number,
                owner_name,
                0,
                rate
            )

        elif account_type == "2":

            limit = float(input("Hạn mức tín dụng: "))

            current_account = CreditAccount(
                account_number,
                owner_name,
                0,
                limit
            )

        elif account_type == "3":

            rate = float(input("Lãi suất: "))

            current_account = HybridAccount(
                account_number,
                owner_name,
                0,
                rate
            )

        else:
            print("Không hợp lệ")
            continue

        accounts.append(current_account)

        print("Mở tài khoản thành công")

    elif choice == "2":

        if current_account is None:
            print("Chưa có tài khoản")
            continue

        print("\nLoại:",
              current_account.__class__.__name__)

        print("Tên:",
              current_account.owner_name)

        print("Số dư:",
              f"{current_account.balance:,.0f}")

        print("\nMRO:")

        for cls in current_account.__class__.mro():
            print(cls.__name__)

    elif choice == "3":

        if current_account is None:
            print("Chưa có tài khoản")
            continue

        print("1. Nạp")
        print("2. Rút")

        action = input("Chọn: ")

        amount = float(input("Số tiền: "))

        if action == "1":

            current_account.deposit(amount)

            if isinstance(current_account, HybridAccount):

                cashback = current_account.cashback_reward(amount)

                if cashback > 0:
                    current_account.deposit(cashback)

                    print(
                        f"Hoàn tiền: {cashback:,.0f}"
                    )

        elif action == "2":

            current_account.withdraw(amount)

        print(
            f"Số dư hiện tại: "
            f"{current_account.balance:,.0f}"
        )

    elif choice == "4":

        if isinstance(
            current_account,
            (SavingsAccount, HybridAccount)
        ):

            interest = current_account.apply_interest()

            print(
                f"Tiền lãi: "
                f"{interest:,.0f}"
            )

            print(
                f"Số dư mới: "
                f"{current_account.balance:,.0f}"
            )

        else:
            print(
                "Tài khoản tín dụng "
                "không hỗ trợ tính lãi"
            )

    elif choice == "5":

        if len(accounts) < 2:
            print("Cần ít nhất 2 tài khoản")
            continue

        print("\nDanh sách tài khoản:")

        for i, acc in enumerate(accounts):
            print(
                i,
                acc.owner_name,
                f"({acc.balance:,.0f})"
            )

        index = int(
            input(
                "Chọn tài khoản đối ứng: "
            )
        )

        other = accounts[index]

        print(
            "\nKết quả so sánh:"
        )

        print(
            current_account < other
        )

        print(
            "Tổng số dư:",
            current_account + other
        )

    elif choice == "6":

        if current_account is None:
            print("Chưa có tài khoản")
            continue

        print("1. VNPay")
        print("2. Viettel Money")

        gateway_choice = input("Chọn: ")

        amount = float(
            input("Số tiền hóa đơn: ")
        )

        if gateway_choice == "1":
            gateway = VNPayGateway()

        else:
            gateway = ViettelMoneyGateway()

        process_payment(
            gateway,
            current_account,
            amount
        )

        print(
            "Số dư còn lại:",
            f"{current_account.balance:,.0f}"
        )

    elif choice == "7":

        print("Cảm ơn đã sử dụng chương trình")
        break

    else:
        print("Lựa chọn không hợp lệ")