/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    bool check(map<int, int> &mp){
        int odd = 0;
        for(auto [x, y] : mp){
            if(y%2 == 1){
                odd++;
            }
            if(odd >= 2){
                return false;
            }
        }
        return true;
    }
    map<int, int> mp;
    int ans = 0;
    void solve(TreeNode* root){
        if(root == NULL){
            return;
        }
        mp[root->val]++;
        if(root->left == NULL && root->right == NULL){
            if(check(mp)){
                ans++;
            }
        }
        solve(root->left);
        solve(root->right); 
        mp[root->val]--; 
    }
    int pseudoPalindromicPaths (TreeNode* root) {
        solve(root); 
        return ans;
    }
};