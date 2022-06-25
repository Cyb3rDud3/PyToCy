
def recursive_fibo(n: int) -> int:
    if n <=1:
        return n
    return recursive_fibo(n-1) + recursive_fibo(n-2)

def main() -> None:
    for i in range(50):
        x = recursive_fibo(i)



if __name__ == "__main__":
    main()