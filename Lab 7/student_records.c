#include <stdio.h>
#include <string.h>

#define MAX 50
#define SUBJECTS 5

typedef struct {
    char name[30];
    int marks[SUBJECTS];
    float avg;
    char grade;
} Student;

float calcAverage(int marks[]) {
    int sum = 0;
    for (int i = 0; i < SUBJECTS; i++)
        sum += marks[i];
    return sum / (float)SUBJECTS;
}

char assignGrade(float avg) {
    if (avg >= 90) return 'A';
    else if (avg >= 75) return 'B';
    else if (avg >= 60) return 'C';
    else if (avg >= 40) return 'D';
    else return 'F';
}

void inputStudent(Student *s) {
    printf("Enter student name: ");
    scanf("%s", s->name);
    printf("Enter marks in %d subjects: ", SUBJECTS);
    for (int i = 0; i < SUBJECTS; i++)
        scanf("%d", &s->marks[i]);
    s->avg = calcAverage(s->marks);
    s->grade = assignGrade(s->avg);
}

void printStudent(Student s) {
    printf("%-15s  ", s.name);
    printf("Avg: %6.2f  Grade: %c\n", s.avg, s.grade);
}

void displayAll(Student s[], int n) {
    printf("\n%-15s  %-10s  %-10s\n", "Name", "Average", "Grade");
    printf("-------------------------------------\n");
    for (int i = 0; i < n; i++)
        printf("%-15s  %8.2f  %5c\n", s[i].name, s[i].avg, s[i].grade);
}

int findStudentIndex(Student s[], int n, char name[]) {
    for (int i = 0; i < n; i++) {
        if (strcmp(s[i].name, name) == 0)
            return i;
    }
    return -1;
}

void updateMarks(Student s[], int n) {
    char name[30];
    printf("Enter name to update marks: ");
    scanf("%s", name);
    int idx = findStudentIndex(s, n, name);
    if (idx == -1) {
        printf("Student not found!\n");
        return;
    }
    printf("Enter new marks for %s:\n", s[idx].name);
    for (int i = 0; i < SUBJECTS; i++)
        scanf("%d", &s[idx].marks[i]);
    s[idx].avg = calcAverage(s[idx].marks);
    s[idx].grade = assignGrade(s[idx].avg);
    printf("Marks updated successfully.\n");
}

void deleteStudent(Student s[], int *n) {
    char name[30];
    printf("Enter name to delete: ");
    scanf("%s", name);
    int idx = findStudentIndex(s, *n, name);
    if (idx == -1) {
        printf("Student not found!\n");
        return;
    }
    for (int i = idx; i < *n - 1; i++) {
        s[i] = s[i + 1];
    }
    (*n)--;
    printf("Record deleted successfully.\n");
}

void sortStudents(Student s[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (s[j].avg < s[j + 1].avg) {
                Student temp = s[j];
                s[j] = s[j + 1];
                s[j + 1] = temp;
            }
        }
    }
    printf("Students sorted by average (descending).\n");
}

void topPerformers(Student s[], int n) {
    if (n == 0) {
        printf("No student records.\n");
        return;
    }
    sortStudents(s, n);
    int limit = (n >= 3) ? 3 : n;
    printf("\nTop %d Performers:\n", limit);
    for (int i = 0; i < limit; i++)
        printStudent(s[i]);
}

float classAverage(Student s[], int n) {
    float total = 0.0;
    for (int i = 0; i < n; i++)
        total += s[i].avg;
    return (n > 0) ? total / n : 0.0;
}

int main() {
    Student s[MAX];
    int n = 0, choice;
    float highest = 0.0;
    char topStudent[30];

    while (1) {
        printf("\n==== STUDENT RECORD SYSTEM ====\n");
        printf("1. Add New Student\n");
        printf("2. Display All Students\n");
        printf("3. Update Marks\n");
        printf("4. Delete Student\n");
        printf("5. Sort by Average\n");
        printf("6. Top Performers\n");
        printf("7. Search Student\n");
        printf("8. Show Class Stats\n");
        printf("9. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        if (choice == 1) {
            if (n >= MAX) {
                printf("Maximum student limit reached.\n");
            } else {
                inputStudent(&s[n]);
                n++;
                printf("Student added successfully.\n");
            }
        } else if (choice == 2) {
            if (n == 0)
                printf("No records to display.\n");
            else
                displayAll(s, n);
        } else if (choice == 3) {
            updateMarks(s, n);
        } else if (choice == 4) {
            deleteStudent(s, &n);
        } else if (choice == 5) {
            if (n > 1)
                sortStudents(s, n);
            else
                printf("Not enough students to sort.\n");
        } else if (choice == 6) {
            topPerformers(s, n);
        } else if (choice == 7) {
            char search[30];
            printf("Enter name to search: ");
            scanf("%s", search);
            int idx = findStudentIndex(s, n, search);
            if (idx != -1)
                printStudent(s[idx]);
            else
                printf("Student not found.\n");
        } else if (choice == 8) {
            if (n == 0) {
                printf("No students yet.\n");
            } else {
                float avg = classAverage(s, n);
                int pass = 0, fail = 0;
                for (int i = 0; i < n; i++) {
                    if (s[i].grade == 'F')
                        fail++;
                    else
                        pass++;
                }
                printf("\nClass Average: %.2f\nPassed: %d | Failed: %d\n", avg, pass, fail);
                // find highest
                highest = 0.0;
                for (int i = 0; i < n; i++) {
                    if (s[i].avg > highest) {
                        highest = s[i].avg;
                        strcpy(topStudent, s[i].name);
                    }
                }
                printf("Top Student: %s (%.2f)\n", topStudent, highest);
            }
        } else if (choice == 9) {
            printf("Exiting program...\n");
            break;
        } else {
            printf("Invalid choice, try again.\n");
        }
    }

    return 0;
}
