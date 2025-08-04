#include <stdio.h>
#include <stdbool.h>
#include <assert.h>

int main() {
    printf("Motivating Example\n");

	int PINSize = 4;
	int PINCandidate[] = {1,2,3,4};
	int PINTrue[] = {4,3,2,1};

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
	
	printf("Grant Access?: %s\n", grantAccess ? "true" : "false");
	printf("Bad Value?: %s\n", badValue ? "true" : "false");
	
	assert(!(grantAccess == true && PINCandidate != PINTrue));
	// assert that logic not broken, err if broken
	return 0;
}


