#include <stdio.h>

#define MAX 100

void bubbleSort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

void insertionSort(int arr[], int n) {
    for (int i = 1; i < n; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

int binarySearch(int arr[], int n, int target) {
    int low = 0, high = n - 1;
    while (low <= high) {
        int mid = (low + high) / 2;
        if (arr[mid] == target)
            return mid;
        else if (arr[mid] < target)
            low = mid + 1;
        else
            high = mid - 1;
    }
    return -1;
}

void display(int arr[], int n) {
    for (int i = 0; i < n; i++)
        printf("%d ", arr[i]);
    printf("\n");
}

int main() {
    int arr[MAX], n, choice, target;

    printf("Enter number of elements (<=100): ");
    scanf("%d", &n);
    if (n <= 0 || n > MAX) {
        printf("Invalid size.\n");
        return 0;
    }

    printf("Enter %d elements:\n", n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }

    while (1) {
        printf("\nMenu:\n1. Bubble Sort\n2. Insertion Sort\n3. Binary Search\n4. Display\n5. Exit\nEnter choice: ");
        scanf("%d", &choice);

        if (choice == 1) {
            bubbleSort(arr, n);
            printf("Array sorted using Bubble Sort.\n");
        } else if (choice == 2) {
            insertionSort(arr, n);
            printf("Array sorted using Insertion Sort.\n");
        } else if (choice == 3) {
            printf("Enter element to search: ");
            scanf("%d", &target);
            int index = binarySearch(arr, n, target);
            if (index != -1)
                printf("Element found at index %d\n", index);
            else
                printf("Element not found.\n");
        } else if (choice == 4) {
            display(arr, n);
        } else if (choice == 5) {
            printf("Exiting program.\n");
            break;
        } else {
            printf("Invalid choice.\n");
        }
    }

    return 0;
}
