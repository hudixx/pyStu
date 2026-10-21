from __future__ import annotations

class OrderId:

    def __init__(self, value: str) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrderId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


def main() -> None:
    order1 = OrderId("A-1")
    order2 = OrderId("A-1")
    print("相等:", order1 == order2)
    print("是否为同一个对象:", order1 is order2)
    set1 = {order1, order2}
    print(len(set1))
    order1.value = "A-2"
    order2.value = "A-3"

    print("改过之后set中的元素值：", next(iter(set1)).value)

    print("改过之后", order1 in set1, any(item is order1 for item in set1))


if __name__ == "__main__":
    main()




