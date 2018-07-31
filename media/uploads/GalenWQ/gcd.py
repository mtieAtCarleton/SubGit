import sys

def getNum():
    num = None

    while num == None:
        try:
            num = int(input())
        except Exception as e:
            print("Please enter an integer input.", end=" ")

    return num

def findGCD(int1, int2):
    for i in range(min(int1, int2), 0, -1):
        if int1 % i == 0 and int2 % i == 0:
            return i

def findGCD2(a, b):
    while b != 0:
        t = b
        b = a % b
        a = t
    return a


def main():
    print("Enter two integers and I'll find their GCD!")

    print("First integer:", end=" ")
    num1 = getNum()
    print("Second integer:", end=" ")
    num2 = getNum()


    print("The gcd of", num1, "and", num2, "is", findGCD(num1, num2))

if __name__ == '__main__':
    main()
