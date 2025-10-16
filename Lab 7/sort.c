#include <stdio.h>

#define MAX 100

// Function declarations
void bubbleSort(int arr[], int n, int ascending);
void insertionSort(int arr[], int n, int ascending);
void selectionSort(int arr[], int n, int ascending);
void mergeSort(int arr[], int l, int r, int ascending);
void merge(int arr[], int l, int m, int r, int ascending);
int binarySearch(int arr[], int n, int target);
int linearSearch(int arr[], int n, int target);
void display(int arr[], int n);
void reverseArray(int arr[], int n);
int findMin(int arr[], int n);
int findMax(int arr[], int n);
int isSorted(int arr[], int n, int ascending);
void swap(int *a, int *b);

// Bubble Sort
void bubbleSort(int arr[], int n, int ascending) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            int condition = ascending ? (arr[j] > arr[j + 1]) : (arr[j] < arr[j + 1]);
            if (condition) {
                swap(&arr[j], &arr[j + 1]);
            }
        }
    }
}

// Insertion Sort
void insertionSort(int arr[], int n, int ascending) {
    for (int i = 1; i < n; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && (ascending ? arr[j] > key : arr[j] < key)) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

// Selection Sort
void selectionSort(int arr[], int n, int ascending) {
    for (int i = 0; i < n - 1; i++) {
        int idx = i;
        for (int j = i + 1; j < n; j++) {
            if (ascending ? arr[j] < arr[idx] : arr[j] > arr[idx]) {
                idx = j;
            }
        }
        if (idx != i) swap(&arr[i], &arr[idx]);
    }
}

// Merge helper
void merge(int arr[], int l, int m, int r, int ascending) {
    int n1 = m - l + 1, n2 = r - m;
    int left[MAX], right[MAX];

    for (int i = 0; i < n1; i++) left[i] = arr[l + i];
    for (int j = 0; j < n2; j++) right[j] = arr[m + 1 + j];

    int i = 0, j = 0, k = l;

    while (i < n1 && j < n2) {
        if (ascending ? left[i] <= right[j] : left[i] >= right[j])
            arr[k++] = left[i++];
        else
            arr[k++] = right[j++];
    }
    while (i < n1) arr[k++] = left[i++];
    while (j < n2) arr[k++] = right[j++];
}

// Merge Sort
void mergeSort(int arr[], int l, int r, int ascending) {
    if (l < r) {
        int m = (l + r) / 2;
        mergeSort(arr, l, m, ascending);
        mergeSort(arr, m + 1, r, ascending);
        merge(arr, l, m, r, ascending);
    }
}

// Binary Search (for sorted arrays)
int binarySearch(int arr[], int n, int target) {
    int low = 0, high = n - 1;
    while (low <= high) {
        int mid = (low + high) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}

// Linear Search
int linearSearch(int arr[], int n, int target) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == target) return i;
    }
    return -1;
}

// Reverse Array
void reverseArray(int arr[], int n) {
    for (int i = 0; i < n / 2; i++) {
        swap(&arr[i], &arr[n - i - 1]);
    }
}

// Find minimum element
int findMin(int arr[], int n) {
    int min = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] < min) min = arr[i];
    }
    return min;
}

// Find maximum element
int findMax(int arr[], int n) {
    int max = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > max) max = arr[i];
    }
    return max;
}

// Check if sorted
int isSorted(int arr[], int n, int ascending) {
    for (int i = 0; i < n - 1; i++) {
        if (ascending && arr[i] > arr[i + 1]) return 0;
        if (!ascending && arr[i] < arr[i + 1]) return 0;
    }
    return 1;
}

// Swap helper
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

// Display array
void display(int arr[], int n) {
    for (int i = 0; i < n; i++)
        printf("%d ", arr[i]);
    printf("\n");
}

// Main function
int main() {
    int arr[MAX], n, choice, target, ascending = 1;

    printf("Enter number of elements (<=100): ");
    scanf("%d", &n);
    if (n <= 0 || n > MAX) {
        printf("Invalid size.\n");
        return 0;
    }

    printf("Enter %d elements:\n", n);
    for (int i = 0; i < n; i++) scanf("%d", &arr[i]);

    while (1) {
        printf("\n=== MENU ===\n");
        printf("1. Bubble Sort\n");
        printf("2. Insertion Sort\n");
        printf("3. Selection Sort\n");
        printf("4. Merge Sort\n");
        printf("5. Binary Search\n");
        printf("6. Linear Search\n");
        printf("7. Find Min & Max\n");
        printf("8. Check whether Sorted\n");
        printf("9. Reverse Array\n");
        printf("10. Display\n");
        printf("11. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        if (choice >= 1 && choice <= 4) {
            printf("Sort order (1=Ascending, 0=Descending): ");
            scanf("%d", &ascending);
        }

        switch (choice) {
            case 1:
                bubbleSort(arr, n, ascending);
                printf("Array sorted using Bubble Sort.\n");
                break;
            case 2:
                insertionSort(arr, n, ascending);
                printf("Array sorted using Insertion Sort.\n");
                break;
            case 3:
                selectionSort(arr, n, ascending);
                printf("Array sorted using Selection Sort.\n");
                break;
            case 4:
                mergeSort(arr, 0, n - 1, ascending);
                printf("Array sorted using Merge Sort.\n");
                break;
            case 5:
                printf("Enter element to search: ");
                scanf("%d", &target);
                if (!isSorted(arr, n, 1)) {
                    printf("Array not sorted ascending! Sorting first...\n");
                    bubbleSort(arr, n, 1);
                }
                int idx1 = binarySearch(arr, n, target);
                if (idx1 != -1) printf("Element found at index %d\n", idx1);
                else printf("Element not found.\n");
                break;
            case 6:
                printf("Enter element to search: ");
                scanf("%d", &target);
                int idx2 = linearSearch(arr, n, target);
                if (idx2 != -1) printf("Element found at index %d\n", idx2);
                else printf("Element not found.\n");
                break;
            case 7:
                printf("Min = %d, Max = %d\n", findMin(arr, n), findMax(arr, n));
                break;
            case 8:
                if (isSorted(arr, n, 1))
                    printf("Array is sorted in ascending order.\n");
                else if (isSorted(arr, n, 0))
                    printf("Array is sorted in descending order.\n");
                else
                    printf("Array is not sorted.\n");
                break;
            case 9:
                reverseArray(arr, n);
                printf("Array reversed.\n");
                break;
            case 10:
                display(arr, n);
                break;
            case 11:
                printf("Exiting program.\n");
                return 0;
            default:
                printf("Invalid choice.\n");
        }
    }
    return 0;
}
