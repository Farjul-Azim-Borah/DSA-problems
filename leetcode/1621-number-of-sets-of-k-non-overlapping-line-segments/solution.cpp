class Solution {
public:
    int mod = 1e9 + 7;

    int dp[1005][1005][2];

    int solve(int i, int k, int open, int n) {

        if(k < 0)
            return 0;

        if(i == n - 1) {
            if(k == 0)
                return 1;

            return 0;
        }

        if(dp[i][k][open] != -1)
            return dp[i][k][open];

        int ans = 0;

        ans = solve(i + 1, k, 0, n);

        if(open == 0) {
            ans = (ans + solve(i + 1, k - 1, 1, n)) % mod;

        }
        else {
            ans = (ans + solve(i + 1, k, 1, n)) % mod;
            ans = (ans + solve(i + 1, k - 1, 1, n)) % mod;
        }

        return dp[i][k][open] = ans;
    }

    int numberOfSets(int n, int k) {

        memset(dp, -1, sizeof(dp));

        return solve(0, k, 0, n);
    }
};