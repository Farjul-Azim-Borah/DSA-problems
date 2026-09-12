class Solution {
public:
    bool reportSpam(vector<string>& message, vector<string>& bannedWords) {
        map<string , int> mp;
        for(auto i : bannedWords){
            mp[i]++;
        }
        int res = 0; 
        for(auto i : message){
            if(mp.count(i)){
                res++;
            }
            if(res > 1){
                return true;
            }
        }
        return false;
    }
};