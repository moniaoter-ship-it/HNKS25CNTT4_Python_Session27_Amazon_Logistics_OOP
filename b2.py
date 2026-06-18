from abc import ABC, abstractmethod


class BaseProduct(ABC):
    warehouse_name = "Amazon Logistics"
    base_storage_fee = 5000

    def __init__(self, product_code, product_name):
        self.product_code = product_code
        self.product_name = product_name.strip().upper()
        self.__stock_quantity = 0

    @property
    def stock_quantity(self):
        return self.__stock_quantity

    def _set_stock(self, quantity):
        self.__stock_quantity = quantity

    @abstractmethod
    def import_stock(self, quantity):
        pass

    @abstractmethod
    def export_stock(self, quantity):
        pass

    def __add__(self, other):
        if not isinstance(other, BaseProduct):
            return NotImplemented
        return self.stock_quantity + other.stock_quantity

    def __lt__(self, other):
        if not isinstance(other, BaseProduct):
            return NotImplemented
        return self.stock_quantity < other.stock_quantity

    @staticmethod
    def validate_product_code(code):
        return len(code) == 10 and code[0].isalpha()

    @classmethod
    def update_warehouse_name(cls, new_name):
        cls.warehouse_name = new_name


class ColdStorageProduct(BaseProduct):
    def __init__(self, product_code, product_name, temperature):
        super().__init__(product_code, product_name)
        self.required_temperature = temperature

    def import_stock(self, quantity):
        self._set_stock(self.stock_quantity + quantity)

    def export_stock(self, quantity):
        total = quantity * 1.05

        if total > self.stock_quantity:
            print("Không đủ hàng!")
            return

        self._set_stock(self.stock_quantity - total)
        print("Xuất kho thành công!")

    def apply_cooling_cost(self):
        return self.stock_quantity * 3000


class HazardousProduct(BaseProduct):
    def __init__(self, product_code, product_name, limit):
        super().__init__(product_code, product_name)
        self.max_safety_limit = limit

    def import_stock(self, quantity):
        if self.stock_quantity + quantity > self.max_safety_limit:
            print("Vượt giới hạn an toàn!")
            return

        self._set_stock(self.stock_quantity + quantity)

    def export_stock(self, quantity):
        if quantity > self.stock_quantity:
            print("Không đủ hàng!")
            return

        self._set_stock(self.stock_quantity - quantity)


class HybridPremiumProduct(ColdStorageProduct, HazardousProduct):
    def __init__(self, product_code, product_name,
                 temperature, limit):
        ColdStorageProduct.__init__(
            self,
            product_code,
            product_name,
            temperature
        )
        self.max_safety_limit = limit

    def import_stock(self, quantity):
        if self.stock_quantity + quantity > self.max_safety_limit:
            print("Vượt giới hạn an toàn!")
            return

        self._set_stock(self.stock_quantity + quantity)


class FedExCarrier:
    def ship_package(self, product, quantity):
        print(
            f"FedEx vận chuyển {quantity} sản phẩm {product.product_code}"
        )


class DHLCarrier:
    def ship_package(self, product, quantity):
        print(
            f"DHL vận chuyển {quantity} sản phẩm {product.product_code}"
        )


def dispatch_to_carrier(carrier, product, quantity):
    try:
        carrier.ship_package(product, quantity)
        product.export_stock(quantity)
    except AttributeError:
        print("Đơn vị vận chuyển không hợp lệ!")


products = []
current_product = None

while True:
    print("\n===== AMAZON INVENTORY =====")
    print("1. Tạo sản phẩm")
    print("2. Xem thông tin")
    print("3. Nhập/Xuất kho")
    print("4. Tính phí làm lạnh")
    print("5. So sánh & cộng tồn kho")
    print("6. Vận chuyển")
    print("7. Thoát")

    choice = input("Chọn: ")

    if choice == "1":
        print("1. Cold")
        print("2. Hazardous")
        print("3. Hybrid")

        product_type = input("Loại: ")

        code = input("Mã sản phẩm: ")

        if not BaseProduct.validate_product_code(code):
            print("Mã không hợp lệ!")
            continue

        name = input("Tên sản phẩm: ")

        if product_type == "1":
            temp = int(input("Nhiệt độ: "))
            current_product = ColdStorageProduct(
                code,
                name,
                temp
            )

        elif product_type == "2":
            limit = int(input("Giới hạn: "))
            current_product = HazardousProduct(
                code,
                name,
                limit
            )

        elif product_type == "3":
            temp = int(input("Nhiệt độ: "))
            limit = int(input("Giới hạn: "))
            current_product = HybridPremiumProduct(
                code,
                name,
                temp,
                limit
            )

        products.append(current_product)
        print("Tạo thành công!")

    elif choice == "2":
        if current_product is None:
            print("Chưa có sản phẩm!")
            continue

        print("Loại:", type(current_product).__name__)
        print("Mã:", current_product.product_code)
        print("Tên:", current_product.product_name)
        print("Tồn kho:", current_product.stock_quantity)

        print("MRO:")
        for cls in type(current_product).mro():
            print(cls.__name__)

    elif choice == "3":
        if current_product is None:
            print("Chưa có sản phẩm!")
            continue

        action = input("1.Nhập 2.Xuất: ")
        quantity = int(input("Số lượng: "))

        if action == "1":
            current_product.import_stock(quantity)
        else:
            current_product.export_stock(quantity)

    elif choice == "4":
        if isinstance(
                current_product,
                (ColdStorageProduct, HybridPremiumProduct)
        ):
            print(
                "Chi phí:",
                current_product.apply_cooling_cost()
            )
        else:
            print("Không hỗ trợ!")

    elif choice == "5":
        if len(products) < 2:
            print("Cần ít nhất 2 sản phẩm!")
            continue

        other = products[0]

        if other == current_product:
            other = products[1]

        print("Tổng tồn kho:", current_product + other)

        if current_product < other:
            print("Tồn kho hiện tại ít hơn")

    elif choice == "6":
        if current_product is None:
            print("Chưa có sản phẩm!")
            continue

        print("1. FedEx")
        print("2. DHL")

        carrier_choice = input("Chọn: ")
        quantity = int(input("Số lượng: "))

        if carrier_choice == "1":
            carrier = FedExCarrier()
        else:
            carrier = DHLCarrier()

        dispatch_to_carrier(
            carrier,
            current_product,
            quantity
        )

    elif choice == "7":
        print("Tạm biệt!")
        break