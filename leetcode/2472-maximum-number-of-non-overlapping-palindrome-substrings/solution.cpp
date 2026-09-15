class Solution {
public:
    int palin[2001][2001]; 
    
    void isp(string s){
        int n = s.size();
        for(int i = 0; i<n; ++i){
            palin[i][i] = 1;
        }
        for(int i = 0; i<n-1; ++i){
            if(s[i] == s[i+1]){
                palin[i][i+1] = 1;
            }
        }
        for(int len = 3; len <= n; ++len){
            for(int i = 0; i<n; ++i){
                int j = i+len-1;
                if(j >= n){
                    continue;
                }
                if(s[i] == s[j] && palin[i+1][j-1] == 1){
                    palin[i][j] = 1;
                }
            }
        }
    }
    int dp[2001];
    int solve(int i, string &s, int n, int k){
        if(i >= n){
            return 0;
        }
        if(dp[i] != -1){
            return dp[i]; 
        }
        int ans = 0;
        for(int r = i+k-1; r<n; ++r){
            if(palin[i][r] == 1){
                ans = max(ans, 1 + solve(r+1, s, n, k));
            }
        }
        ans = max(ans, solve(i+1, s, n, k));
        return dp[i] = ans; 
    }
    int maxPalindromes(string s, int k) {
        isp(s);
        int n = s.size();
        memset(dp, -1, sizeof(dp)); 
        return solve(0, s, n, k); 
    }
};