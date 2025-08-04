#include <stdio.h>
#include <stdbool.h>
#include <assert.h>

int main() {
	int PINSize = 4;
	int PINCandidate[] = {0,0,0,0};
	int PINTrue[] = {1,2,3,4};

	bool grantAccess = false;
	bool badValue = false;
	int i = 0;
	while (i < PINSize) {
		if (PINCandidate[i] != PINTrue[i]) {
			badValue = true;
		}
		i++;
	}	
	if (badValue == false) {
		grantAccess = true;
	}
	
	if (grantAccess) {
        printf("Access Granted");
    } else {
        printf("Access Denied");
    }
	assert(!(grantAccess == true && PINCandidate != PINTrue));
	return 0;
}