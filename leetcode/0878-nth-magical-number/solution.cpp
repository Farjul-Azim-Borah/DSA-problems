class Solution {
public:
    long long gcd(long long a, long long b) {
        return (b == 0) ? a : gcd(b, a % b);
    }
    long long lcm(long long a, long long b) { return (a / gcd(a, b)) * b; }

    long long noOfMultiples(long long val, long long a, long long b) {
        long long lcmAB = lcm(a, b);
        return (val / a + val / b - val / lcmAB);
    }
    int nthMagicalNumber(int n, int a, int b) {
        const int M = 1e9 + 7;
        long long varA = a;
        long long varB = b;
        long long start = 1, end = 1e18;
        long long nthMagicNum;
        while (start <= end) {
            long long mid = start + (end - start) / 2;
            if (noOfMultiples(mid, varA, varB) >= n) {
                nthMagicNum = mid;
                end = mid - 1;
            } else
                start = mid + 1;
        }

        return (int)(nthMagicNum % M);
    }
};