#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdarg.h>
#include <time.h>

#define HASH_CAPACITY 67
#define bool int
#define true 1
#define false 0
#define PI createNumber(3.141592653589793)   
#define E createNumber(2.718281828459045) 

//####################################################################################################
//############################################# E R R O R ############################################
//####################################################################################################

void throwError(const char *message) {
    fprintf(stderr, "Error: %s\n", message);
    exit(1);
}

//####################################################################################################
//############################################# T Y P E S ############################################
//####################################################################################################

typedef struct Attribute
{
    char* key;
    void* value;
    struct Attribute* next;
} Attribute;
 
typedef struct Object {
    Attribute** lists;
} Object;


unsigned int hash(char* key, int capacity) {
    unsigned long hash = 5381;
    int h;

    while ((h = *key++))
        hash = ((hash << 5) + hash) + h; 

    return hash % capacity;
}

void setAttribute(Object* obj, char* key, void* value) {
    if(obj == NULL || obj->lists == NULL)
        throwError("Null Reference");

    unsigned int index = hash(key, HASH_CAPACITY);
    Attribute* att = malloc(sizeof(Attribute));
    att->key = strdup(key);
    att->value = value;
    att->next = obj->lists[index];
    obj->lists[index] = att;
}

Attribute* getAttribute(Object* obj, char* key) {
    if(obj == NULL || obj->lists == NULL)
        throwError("Null Reference");

    unsigned int index = hash(key, HASH_CAPACITY);
    Attribute* current = obj->lists[index];

    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current;
        }
        current = current->next;
    }
    
    return NULL;
}

void* getAttributeValue(Object* obj, char* key) {
    if(obj == NULL || obj->lists == NULL)
        throwError("Null Reference");

    unsigned int index = hash(key, HASH_CAPACITY);
    Attribute* current = obj->lists[index];

    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current->value;
        }
        current = current->next;
    }
    
    return NULL;
}

void updateAttributeValue(Object* obj, char* key, void* value) {
    if(obj == NULL || obj->lists == NULL)
        throwError("Null Reference");

    Attribute* att = getAttribute(obj, key);
    free(att->value);
    att->value = value;
}


void removeAttribute(Object* obj, char* key) {
    if(obj == NULL || obj->lists == NULL)
        throwError("Null Reference");

    unsigned int index = hash(key, HASH_CAPACITY);
    Attribute* current = obj->lists[index];
    Attribute* previous = NULL;

    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            if (previous == NULL) {
                obj->lists[index] = current->next;
            } else {
                previous->next = current->next;
            }
            free(current->key);
            free(current->value);
            free(current);
            return;
        }
        previous = current;
        current = current->next;
    }
}


//####################################################################################################
//################################ M E T H O D  D E C L A R A T I O N ################################
//####################################################################################################

// Object
Object* createEmptyObject();
Object* createObject();
Object* replaceObject(Object* destination, Object* origin);
Object* copyObject(Object* obj);
Object* method_Object_equals(Object* obj1, Object* obj2);
Object* method_Object_toString(Object* obj);

// Dynamic

void* getMethodForCurrentType(Object* obj, char* method_name, char* base_type);
char* getType(Object* obj);
Object* isType(Object* obj, char* type);
Object* isProtocol(Object* obj, char* protocol);


// Print
Object* function_print(Object* obj);

// Number
Object* createNumber(double number);
Object* method_Number_toString(Object* number);
Object* method_Number_equals(Object* left, Object* right);
Object* numberSum(Object* left, Object* right);
Object* numberMinus(Object* left, Object* right);
Object* numberMultiply(Object* left, Object* right);
Object* numberDivision(Object* left, Object* right);
Object* numberPow(Object* left, Object* right);
Object* function_sqrt(Object* number);
Object* function_sin(Object* angle);
Object* function_cos(Object* angle);
Object* function_exp(Object* number);
Object* function_log(Object* number);
Object* function_rand();
Object* numberGreaterThan(Object* left, Object* right);
Object* numberGreaterOrEqualThan(Object* left, Object* right);
Object* numberLessThan(Object* left, Object* right);
Object* numberLessOrEqualThan(Object* left, Object* right);
Object* numberMod(Object* left, Object* right);
Object* function_parse(Object* string);


// String
Object* createString(char* str);
Object* stringConcat(Object* string1, Object* string2);
Object* stringDoubleConcat(Object* string1, Object* string2);
Object* method_String_size(Object* self);
Object* method_String_toString(Object* str);
Object* method_String_equals(Object* string1, Object* string2);


// Boolean
Object* createBoolean(bool boolean);
Object* method_Boolean_toString(Object* boolean);
Object* method_Boolean_equals(Object* bool1, Object* bool2);
Object* negBoolean(Object* boolean);
Object* boolOr(Object* bool1, Object* bool2);
Object* boolAnd(Object* bool1, Object* bool2);


// Vector
Object* createVectorFromList(int num_elements, Object** list);
Object* createVector(int num_elements, ...);
Object* method_Vector_size(Object* self);
Object* method_Vector_next(Object* self);
Object* method_Vector_current(Object* self);
Object* getElementOfVector(Object* vector, Object* index);
Object* method_Vector_toString(Object* vector);
Object* method_Vector_equals(Object* vector1, Object* vector2);

//Range
Object* function_range(Object* start, Object* end);
Object* createRange(Object* min, Object* max);
Object* method_Range_next(Object* self);
Object* method_Range_current(Object* self);
Object* method_Range_toString(Object* range);
Object* method_Range_toString(Object* range);
Object* method_Range_equals(Object* range1, Object* range2);

//####################################################################################################
//################################# M E T H O D  D E F I N I T I O N #################################
//####################################################################################################

//####################################################################################################
//############################################ O B J E C T ###########################################
//####################################################################################################

Object* createEmptyObject(){
    return malloc(sizeof(Object));
}

Object* createObject() {
    Object* obj = createEmptyObject();
    
    obj->lists = malloc(sizeof(Attribute*) * HASH_CAPACITY);
    for (int i = 0; i < HASH_CAPACITY; i++) {
        obj->lists[i] = NULL;
    }

    setAttribute(obj, "parent_type0", "Object");
    setAttribute(obj, "parent_type1", "Null");
    setAttribute(obj, "method_Object_toString", *method_Object_toString);
    setAttribute(obj, "method_Object_equals", *method_Object_equals);
    return obj;
}

Object* replaceObject(Object* destination, Object* origin)
{
    if(destination == NULL && origin != NULL)
        destination = copyObject(origin);
    
    else if(destination != NULL && origin == NULL)
        destination->lists = NULL;

    else if(destination != NULL && origin != NULL)
        destination->lists = origin->lists;

    return destination;
}

Object* copyObject(Object* obj) {
    return replaceObject(createEmptyObject(), obj);
}


Object* method_Object_equals(Object* obj1, Object* obj2)
{
    return createBoolean(obj1 == obj2);
}


Object* method_Object_toString(Object* obj)
{
    char* addr = malloc(50); 
    sprintf(addr, "%p", (void*)obj);

    return createString(addr);
}


//####################################################################################################
//########################################### D Y N A M I C ##########################################
//####################################################################################################


void* getMethodForCurrentType(Object* obj, char* method_name, char* base_type)
{
    if(obj == NULL)
        throwError("Null Reference");

    bool found_base_type = base_type == NULL;

    int index = 0;
    char* initial_parent_type = malloc(128);
    sprintf(initial_parent_type, "%s%d", "parent_type", index++);
    char* type = getAttributeValue(obj, initial_parent_type);
    free(initial_parent_type);

    while(type != NULL)
    {
        if(found_base_type || strcmp(type, base_type) == 0)
        {
            found_base_type = true;

            char* full_name = malloc(128);
            sprintf(full_name, "%s%s%s%s", "method_", type, "_", method_name);

            void* method = getAttributeValue(obj, full_name);

            free(full_name);

            if(method != NULL)
                return method;
        }

        char* parent_type = malloc(128);
        sprintf(parent_type, "%s%d", "parent_type", index++);
        type = getAttributeValue(obj, parent_type);
        free(parent_type);
    }

    return NULL;
}

char* getType(Object* obj)
{
    if(obj == NULL)
        throwError("Null Reference");

    return getAttributeValue(obj, "parent_type0");
}


Object* isType(Object* obj, char* type)
{
    if(obj == NULL)
        throwError("Null Reference");

    int index = 0;
    char* initial_parent_type = malloc(128);
    sprintf(initial_parent_type, "%s%d", "parent_type", index++);
    char* ptype = getAttributeValue(obj, initial_parent_type);
    free(initial_parent_type);

    while(ptype != NULL)
    {
        if(strcmp(ptype, type) == 0)
            return createBoolean(true);

        char* parent_type = malloc(128);
        sprintf(parent_type, "%s%d", "parent_type", index++);
        ptype = getAttributeValue(obj, parent_type);
        free(parent_type);
    }

    return createBoolean(false);
}


Object* isProtocol(Object* obj, char* protocol)
{
    if(obj == NULL)
        throwError("Null Reference");

    int index = 0;
    char* initial_protocol = malloc(128);
    sprintf(initial_protocol, "%s%d", "conforms_protocol", index++);
    char* pprotocol = getAttributeValue(obj, initial_protocol);
    free(initial_protocol);

    while(pprotocol != NULL)
    {
        if(strcmp(pprotocol, protocol) == 0)
            return createBoolean(true);

        char* cprotocol = malloc(128);
        sprintf(cprotocol, "%s%d", "conforms_protocol", index++);
        pprotocol = getAttributeValue(obj, cprotocol);
        free(cprotocol);
    }

    return createBoolean(false);
}

//####################################################################################################
//############################################# P R I N T ############################################
//####################################################################################################

Object* function_print(Object* obj)
{
    if(obj == NULL || obj->lists == NULL)
    {
        printf("Null\n");
        return createString("Null");
    }

    Object* str = ((Object* (*)(Object*))getMethodForCurrentType(obj, "toString", NULL))(obj);
    
    char* value = getAttributeValue(str, "value");
    printf("%s\n", value);

    return str;
}


//####################################################################################################
//############################################ N U M B E R ###########################################
//####################################################################################################


Object* createNumber(double number) {
    Object* obj = createObject();

    double* value = malloc(sizeof(double));
    *value = number;

    setAttribute(obj, "value", value);
    setAttribute(obj, "parent_type0", "Number");
    setAttribute(obj, "parent_type1", "Object");
    setAttribute(obj, "method_Number_toString", *method_Number_toString);
    setAttribute(obj, "method_Number_equals", *method_Number_equals);

    return obj;
}

Object* method_Number_toString(Object* number) {
    if(number == NULL)
        throwError("Null Reference");

    double* value = getAttributeValue(number, "value");

    char *str = malloc(30);
    sprintf(str, "%f", *value);
    return createString(str);
}


Object* method_Number_equals(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");

    if(strcmp(getType(left), "Number") != 0 || strcmp(getType(right), "Number") != 0)
        return createBoolean(false);

    double* value1 = getAttributeValue(left, "value");
    double* value2 = getAttributeValue(right, "value");

    return createBoolean(fabs(*value1 - *value2) < 0.0000000001);
}


Object* numberSum(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");

    double* value1 = getAttributeValue(left, "value");
    double* value2 = getAttributeValue(right, "value");

    return createNumber(*value1 + *value2);
}

Object* numberMinus(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");

    double* value1 = getAttributeValue(left, "value");
    double* value2 = getAttributeValue(right, "value");

    return createNumber(*value1 - *value2);
}

Object* numberMultiply(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");

    double* value1 = getAttributeValue(left, "value");
    double* value2 = getAttributeValue(right, "value");

    return createNumber(*value1 * *value2);
}

Object* numberDivision(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");

    double* value1 = getAttributeValue(left, "value");
    double* value2 = getAttributeValue(right, "value");

    if(*value2 == 0)
        throwError("Zero Division");

    return createNumber(*value1 / *value2);
}

Object* numberPow(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");

    double* value = getAttributeValue(left, "value");
    double* exp = getAttributeValue(right, "value");

    return createNumber(pow(*value, *exp));
}


Object* function_sqrt(Object* number) {
    if(number == NULL)
        throwError("Null Reference");
    
    double* value = getAttributeValue(number, "value");

    return createNumber(sqrt(*value));
}

Object* function_sin(Object* angle) {
    if(angle == NULL)
        throwError("Null Reference");
    
    double* vangle = getAttributeValue(angle, "value");

    return createNumber(sin(*vangle));
}

Object* function_cos(Object* angle) {
    if(angle == NULL)
        throwError("Null Reference");

    double* vangle = getAttributeValue(angle, "value");

    return createNumber(cos(*vangle));
}

Object* function_exp(Object* number) {
    if(number == NULL)
        throwError("Null Reference");

    double* value = getAttributeValue(number, "value");

    return createNumber(exp(*value));
}

Object* function_log(Object* number) {
    if(number == NULL)
        throwError("Null Reference");

    double* value = getAttributeValue(number, "value");

    return createNumber(log(*value));
}

Object* function_rand() {
    return createNumber((double)rand() / (RAND_MAX));
}


Object* numberGreaterThan(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");
    
    double* value1 = getAttributeValue(left, "value");
    double* value2 = getAttributeValue(right, "value");

    return createBoolean(*value1 > *value2);
}

Object* numberGreaterOrEqualThan(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");

    double* value1 = getAttributeValue(left, "value");
    double* value2 = getAttributeValue(right, "value");

    return createBoolean(*value1 >= *value2);
}

Object* numberLessThan(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");

    double* value1 = getAttributeValue(left, "value");
    double* value2 = getAttributeValue(right, "value");

    return createBoolean(*value1 < *value2);
}

Object* numberLessOrEqualThan(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");

    double* value1 = getAttributeValue(left, "value");
    double* value2 = getAttributeValue(right, "value");

    return createBoolean(*value1 <= *value2);
}

Object* numberMod(Object* left, Object* right) {
    if(left == NULL || right == NULL)
        throwError("Null Reference");

    double* value1 = getAttributeValue(left, "value");
    double* value2 = getAttributeValue(right, "value");

    return createNumber(((int)*value1) % ((int)*value2));
}

Object* function_parse(Object* string) {
    if(string == NULL)
        throwError("Null Reference");

    char* value = getAttributeValue(string, "value");
    return createNumber(strtod(value, NULL));
}


//####################################################################################################
//############################################ S T R I N G ###########################################
//####################################################################################################

Object* createString(char* str) {
    Object* obj = createObject();

    setAttribute(obj, "value", str);
    setAttribute(obj, "parent_type0", "String");
    setAttribute(obj, "parent_type1", "Object");

    int *len = malloc(sizeof(int));
    *len = strlen(str);

    setAttribute(obj, "len", len);
    setAttribute(obj, "method_String_toString", *method_String_toString);
    setAttribute(obj, "method_String_equals", *method_String_equals);
    setAttribute(obj, "method_String_size", *method_String_size);

    return obj;
}


Object* stringConcat(Object* obj1, Object* obj2)
{
    if(obj1 == NULL || obj2 == NULL)
        throwError("Null Reference");

    Object* string1 = ((Object* (*)(Object*))getMethodForCurrentType(obj1, "toString", NULL))(obj1);
    Object* string2 = ((Object* (*)(Object*))getMethodForCurrentType(obj2, "toString", NULL))(obj2);

    char* str1 = getAttributeValue(string1, "value");
    int len1 = *(int*)getAttributeValue(string1, "len");

    char* str2 = getAttributeValue(string2, "value");
    int len2 = *(int*)getAttributeValue(string2, "len");

    char* result = malloc((len1 + len2 + 1) * sizeof(char));
    sprintf(result, "%s%s%c", str1, str2,'\0');


    return createString(result);
}

Object* stringDoubleConcat(Object* obj1, Object* obj2)
{
    if(obj1 == NULL || obj2 == NULL)
        throwError("Null Reference");

    Object* string1 = ((Object* (*)(Object*))getMethodForCurrentType(obj1, "toString", NULL))(obj1);
    Object* string2 = ((Object* (*)(Object*))getMethodForCurrentType(obj2, "toString", NULL))(obj2);

    char* str1 = getAttributeValue(string1, "value");
    int len1 = *(int*)getAttributeValue(string1, "len");

    char* str2 = getAttributeValue(string2, "value");
    int len2 = *(int*)getAttributeValue(string2, "len");

    char* result = malloc((len1 + len2 + 2) * sizeof(char));
    sprintf(result, "%s%c%s%c", str1,' ',str2, '\0');

    return createString(result);
}

Object* method_String_size(Object* self) {
    if(self == NULL)
        throwError("Null Reference");

    return createNumber(*(int*)getAttributeValue(self, "len"));
}

Object* method_String_toString(Object* str) {
    if(str == NULL)
        throwError("Null Reference");

    return str;
}


Object* method_String_equals(Object* string1, Object* string2) {
    if(string1 == NULL || string2 == NULL)
        throwError("Null Reference");

    if(strcmp(getType(string1), "String") != 0 || strcmp(getType(string2), "String") != 0)
        return createBoolean(false);

    char* value1 = getAttributeValue(string1, "value");
    char* value2 = getAttributeValue(string2, "value");

    return createBoolean(strcmp(value1, value2) == 0);
}


//####################################################################################################
//############################################## B O O L #############################################
//####################################################################################################

Object* createBoolean(bool boolean) {
    Object* obj = createObject();

    bool* value = malloc(sizeof(bool));
    *value = boolean;

    setAttribute(obj, "value", value);
    setAttribute(obj, "parent_type0", "Boolean");
    setAttribute(obj, "parent_type1", "Object");
    setAttribute(obj, "method_Boolean_toString", *method_Boolean_toString);
    setAttribute(obj, "method_Boolean_equals", *method_Boolean_equals);

    return obj;
}

Object* method_Boolean_toString(Object* boolean) {
    if(boolean == NULL)
        throwError("Null Reference");

    bool* value = getAttributeValue(boolean, "value");

    if(*value == true)
        return createString("true");
    else
        return createString("false");
}

Object* method_Boolean_equals(Object* bool1, Object* bool2) {
    if(bool1 == NULL || bool2 == NULL)
        throwError("Null Reference");

    if(strcmp(getType(bool1), "Boolean") != 0 || strcmp(getType(bool2), "Boolean") != 0)
        return createBoolean(false);

    bool* value1 = getAttributeValue(bool1, "value");
    bool* value2 = getAttributeValue(bool2, "value");

    return createBoolean(value1 == value2);
}


Object* negBoolean(Object* boolean) {
    if(boolean == NULL)
        throwError("Null Reference");

    bool* value = getAttributeValue(boolean, "value");

    return createBoolean(!*value);
}

Object* boolOr(Object* bool1, Object* bool2)
{
    if(bool1 == NULL || bool2 == NULL)
        throwError("Null Reference");

    bool vbool1 = *(bool*)getAttributeValue(bool1, "value");
    bool vbool2 = *(bool*)getAttributeValue(bool2, "value");

    return createBoolean(vbool1 || vbool2);
}

Object* boolAnd(Object* bool1, Object* bool2)
{
    if(bool1 == NULL || bool2 == NULL)
        throwError("Null Reference");

    bool vbool1 = *(bool*)getAttributeValue(bool1, "value");
    bool vbool2 = *(bool*)getAttributeValue(bool2, "value");

    return createBoolean(vbool1 && vbool2);
}


//####################################################################################################
//############################################ V E C T O R ###########################################
//####################################################################################################


Object* createVectorFromList(int num_elements, Object** list)
{
    Object* vector = createObject();

    setAttribute(vector, "parent_type0", "Vector");
    setAttribute(vector, "parent_type1", "Object");

    setAttribute(vector, "conforms_protocol0", "Iterable");

    setAttribute(vector, "method_Vector_toString", *method_Vector_toString);
    setAttribute(vector, "method_Vector_equals", *method_Vector_equals);

    int* size = malloc(sizeof(int));
    *size = num_elements;
    setAttribute(vector, "size", size);

    setAttribute(vector, "list", list);

    setAttribute(vector, "current", createNumber(-1));

    setAttribute(vector, "method_Vector_size", *method_Vector_size);
    setAttribute(vector, "method_Vector_next", *method_Vector_next);
    setAttribute(vector, "method_Vector_current", *method_Vector_current);

    return vector;
}


Object* createVector(int num_elements, ...)
{
    va_list elements;

    va_start(elements, num_elements);

    Object** list = malloc(num_elements * sizeof(Object*));

    for(int i = 0; i < num_elements; i++) {
        list[i] = va_arg(elements, Object*);
    }

    va_end(elements);

    return createVectorFromList(num_elements, list);
}


Object* method_Vector_size(Object* self) {
    if(self == NULL)
        throwError("Null Reference");

    return createNumber(*(int*)getAttributeValue(self, "size"));
}


Object* method_Vector_next(Object* self)
{
    if(self == NULL)
        throwError("Null Reference");

    int size = *(int*)getAttributeValue(self, "size");
    double* current = getAttributeValue((Object*)getAttributeValue(self, "current"), "value");
    
    if(*current + 1 < size) 
    {
        *current += 1;
        return createBoolean(true);
    }

    return createBoolean(false);
}


Object* method_Vector_current(Object* self)
{
    if(self == NULL)
        throwError("Null Reference");

    return getElementOfVector(self, getAttributeValue(self, "current"));
}


Object* getElementOfVector(Object* vector, Object* index)
{
    if(vector == NULL || index == NULL)
        throwError("Null Reference");

    int i = (int)*(double*)getAttributeValue(index, "value");
    int size = *(int*)getAttributeValue(vector, "size");

    if(i >= size)
        throwError("Index out of range");

    return ((Object**)getAttributeValue(vector, "list"))[i];
}


Object* method_Vector_toString(Object* vector)
{
    if(vector == NULL)
        throwError("Null Reference");

    int* size = getAttributeValue(vector, "size");

    int total_size = 3 + ((*size > 0 ? *size : 1) - 1) * 2;

    Object** list = getAttributeValue(vector, "list");

    Object** strs = malloc(*size * sizeof(Object*));

    for(int i = 0; i < *size; i++)
    {
        strs[i] = ((Object* (*)(Object*))getMethodForCurrentType(list[i], "toString", 0))(list[i]);
        total_size += *(int*)getAttributeValue(strs[i], "len");
    }

    char* result = malloc(total_size * sizeof(char));
    result[0] = '\0';

    strcat(result, "[");
    for(int i = 0; i < *size; i++)
    {
        strcat(result, (char*)getAttributeValue(strs[i], "value"));
        free(strs[i]);

        if(i + 1 < *size)
            strcat(result, ", ");
    }
    strcat(result, "]");

    free(strs);

    return createString(result);
}


Object* method_Vector_equals(Object* vector1, Object* vector2)
{
    if(vector1 == NULL || vector2 == NULL)
        throwError("Null Reference");

    if(strcmp(getType(vector1), "Vector") != 0 || strcmp(getType(vector2), "Vector") != 0)
        return createBoolean(false);

    int* size1 = getAttributeValue(vector1, "size");
    Object** list1 = getAttributeValue(vector1, "list");

    int* size2 = getAttributeValue(vector2, "size");
    Object** list2 = getAttributeValue(vector2, "list");

    if(*size1 != *size2)
        return createBoolean(false);

    for(int i = 0; i < *size1; i++)
    {
        bool* equal = getAttributeValue(((Object* (*)(Object*, Object*))getMethodForCurrentType(list1[i], "equals", 0))(list1[i], list2[i]), "value");

        if(!*equal)
            return createBoolean(false);
    }

    return createBoolean(true);
}


//####################################################################################################
//############################################# R A N G E ############################################
//####################################################################################################


Object* function_range(Object* start, Object* end)
{
    if(start == NULL || end == NULL)
        throwError("Null Reference");

    return createRange(start, end);
}


Object* createRange(Object* min, Object* max)
{
    if(min == NULL || max == NULL)
        throwError("Null Reference");

    Object* obj = createObject();

    setAttribute(obj, "min", min);
    setAttribute(obj, "max", max);
    setAttribute(obj, "current", numberMinus(min, createNumber(1)));

    int* size = malloc(sizeof(int));
    *size = (int)(*(double*)getAttributeValue(max, "value")) - (int)(*(double*)getAttributeValue(min, "value"));

    setAttribute(obj, "size", size);

    setAttribute(obj, "parent_type0", "Range");
    setAttribute(obj, "parent_type1", "Object");

    setAttribute(obj, "conforms_protocol0", "Iterable");

    setAttribute(obj, "method_Range_next", *method_Range_next);
    setAttribute(obj, "method_Range_current", *method_Range_current);

    setAttribute(obj, "method_Range_toString", *method_Range_toString);
    setAttribute(obj, "method_Range_equals", *method_Range_equals);

    return obj;
}


Object* method_Range_next(Object* self)
{
    if(self == NULL)
        throwError("Null Reference");

    int max = *(double*)getAttributeValue((Object*)getAttributeValue(self, "max"), "value");
    double* current = getAttributeValue((Object*)getAttributeValue(self, "current"), "value");
    
    if(*current + 1 < max) 
    {
        *current += 1;
        return createBoolean(true);
    }

    return createBoolean(false);
}


Object* method_Range_current(Object* self)
{
    if(self == NULL)
        throwError("Null Reference");

    return getAttributeValue(self, "current");
}


Object* method_Range_toString(Object* range)
{
    if(range == NULL)
        throwError("Null Reference");

    Object* min = getAttributeValue(range, "min");
    Object* max = getAttributeValue(range, "max");

    int total_size = 6;

    Object* min_str = ((Object* (*)(Object*))getMethodForCurrentType(min, "toString", 0))(min);
    total_size += *(int*)getAttributeValue(min_str, "len");

    Object* max_str = ((Object* (*)(Object*))getMethodForCurrentType(max, "toString", 0))(max);
    total_size += *(int*)getAttributeValue(max_str, "len");

    char* result = malloc(total_size * sizeof(char));
    sprintf(result, "[%s - %s]", (char*)getAttributeValue(min_str, "value"), (char*)getAttributeValue(max_str, "value"));

    free(min_str);
    free(max_str);
    return createString(result);
}


Object* method_Range_equals(Object* range1, Object* range2)
{
    if(range1 == NULL || range2 == NULL)
        throwError("Null Reference");

    if(strcmp(getType(range1), "Range") != 0 || strcmp(getType(range2), "Range") != 0)
        return createBoolean(false);

    Object* min1 = getAttributeValue(range1, "min");
    Object* max1 = getAttributeValue(range1, "max");

    Object* min2 = getAttributeValue(range2, "min");
    Object* max2 = getAttributeValue(range2, "max");

    return boolAnd(method_Number_equals(min1, min2), method_Number_equals(max1, max2));
}

//####################################################################################################
//######################################### G E N E R A T E D ########################################
//############################################## C O D E #############################################
//####################################################################################################