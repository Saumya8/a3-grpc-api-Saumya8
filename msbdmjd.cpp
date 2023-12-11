#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <unordered_map>

using namespace std;
// Comparator function to sort product codes based on custom order
bool customComparator(const string &a, const string &b, const unordered_map<char, int> &orderMap) {
    int n = min(a.size(), b.size());
    for (int i = 0; i < n; ++i) {
        if (a[i] != b[i]) {
            return orderMap.at(a[i]) < orderMap.at(b[i]);
        }
    }
    return a.size() < b.size();
}

// Function to sort product codes
void sortProductCodes(vector<string> &productCodes, const string &order) {
    unordered_map<char, int> orderMap;
    for (int i = 0; i < order.size(); ++i) {
        orderMap[order[i]] = i;
    }

    sort(productCodes.begin(), productCodes.end(), [&](const string &a, const string &b) {
        return customComparator(a, b, orderMap);
    });
}