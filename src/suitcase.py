def suitcase(maxVolume, sizes, values, n):

    dp = [[0 for _ in range(maxVolume + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, maxVolume + 1):
            if sizes[i - 1] <= j:
                dp[i][j] = max(values[i - 1] + dp[i - 1][j - sizes[i - 1]], dp[i - 1][j])
            else:
                dp[i][j] = dp[i - 1][j]

    return dp[n][maxVolume]

def main():
    n, maxVolume = map(int, input().split())
    sizes = []
    values = []

    for _ in range(n):
        item, size, value = input().split()
        sizes.append(int(size))
        values.append(int(value))

    maxSatisfaction = suitcase(maxVolume, sizes, values, n)
    print(maxSatisfaction)

if __name__ == "__main__":
    main()
