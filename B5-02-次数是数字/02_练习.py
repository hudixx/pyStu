from __future__ import annotations


class Counter:

    def __init__(self) -> None:

        self._values: dict[str, int] = {}

    def add(self, label: str) -> None:

        current = self._values.get(label, 0)
        self._values[label] = current + 1

    def get(self, label: str) -> int:
        return self._values.get(label, 0)


def main() -> None:

    counter = Counter()
    counter.add("买豆浆")
    counter.add("买牛奶")
    counter.add("买豆浆")
    print("买豆浆", counter.get("买豆浆"))
    print("买牛奶", counter.get("买牛奶"))


if __name__ == "__main__":
    main()

#  题2不知道，请在参考答案的注释中个给出