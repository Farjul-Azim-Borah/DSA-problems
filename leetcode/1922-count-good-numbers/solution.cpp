class Solution {
public:
    long long pow(long long a, long long b, int mod){
        long long ans = 1;
        while(b > 0){
            if(b&1 == 1){
                ans = (ans*a)%mod;
            }
            a = (a*a)%mod;
            b = b/2;
        }
        return ans%mod;
    }
    int countGoodNumbers(long long n) {
        long long ans = 1;
        int mod = 1e9+7;
        if(n%2 == 0){
            long long k = n/2;
            ans = 1ll*(pow(5, k, mod)*pow(4, k, mod))%mod;
        }else{
            long long k = n/2;
            ans = 1ll*(pow(5, k+1, mod)*pow(4, k, mod))%mod;
        }
        
        return ans;
    }
};