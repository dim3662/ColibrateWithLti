import pymysql as pymysql
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import matplotlib.pyplot as plt
from tabulate import tabulate
from decimal import Decimal
from io import StringIO
import numpy as np
import math

from frame.Test import Test

courseNumber = 50


@csrf_exempt
def tests(request):
    if request.method == 'POST':
        print("Post: " + str(request.POST))
        connection = pymysql.connect(host='127.0.0.1',
                                     user='bn_moodle',
                                     password='',
                                     db='bitnami_moodle',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM mdl_question_categories where contextid = " + str(courseNumber)  # ПОМЕНЯТЬ
                cursor.execute(sql)
                # print()
                idCategory = []  # получаем idCategory нашего КУРСА
                for row in cursor:
                    idCategory.append(row['id'])
                # print(idCategory)

                # ищем задания из нашего курса
                taskId = []
                taskIdWithStudents = []
                for id in idCategory:
                    sql = "SELECT * FROM mdl_question where category = " + str(id)
                    cursor.execute(sql)
                    for row in cursor:
                        taskId.append([])
                        taskIdWithStudents.append([])
                        taskId[len(taskId) - 1].append(row['id'])
                        taskIdWithStudents[len(taskId) - 1].append(row['id'])
                        # print(row)  # нащи задания
                # print(taskId)
                # print()
                questionusageid = []
                for id in taskId:
                    sql = "SELECT * FROM mdl_question_attempts where questionid = " + str(id[0])
                    cursor.execute(sql)
                    id.append([])
                    for row in cursor:
                        id[1].append(row['questionusageid'])  # в taskid это будет элемент под индексом 1
                        questionusageid.append(row['questionusageid'])
                # print(len(taskId))
                forDelet = []
                for id in taskId:
                    if len(id[1]) == 0:
                        forDelet.append(id)
                for dele in forDelet:
                    taskId.remove(dele)
                # print()
                # print(len(taskId))
                # print(questionusageid)
                # print(taskId)
                for id in taskId:
                    quizes = set()
                    for i in id[1]:
                        sql = "SELECT * FROM mdl_question_usages where id = " + str(i)
                        cursor.execute(sql)
                        for row in cursor:  # получение разных квизов
                            quizes.add(row['contextid'])
                    id.append(quizes)
                # print(taskId)
                quizes = set()
                for id in taskId:
                    for i in id[2]:
                        quizes.add(i)
                # print(sorted(quizes))
                tests = []  # задания распределены по тестам.
                for contextid in sorted(quizes):
                    tests.append([])
                    for id in taskId:
                        for i in id[2]:
                            if i == contextid:
                                tests[len(tests) - 1].append(id[0])
                print("Тесты: " + str(tests))
                # print(
                #    taskIdWithStudents)  # в каждом списке первая цифра будет айди задания п соледующие айди студентов, кьл его решил
                for number in taskIdWithStudents:
                    sql = "SELECT * FROM mdl_question_attempt_steps where questionattemptid IN (SELECT id FROM mdl_question_attempts where questionid = " + str(
                        number[0]) + ") and state <> 'todo' and state <> 'complete'"
                    cursor.execute(sql)
                    for row in cursor:  # получение разных квизов
                        # print(row)
                        number.append(str(row['userid']) + " " + row['state'])
                # print(taskIdWithStudents)
                quizNames = []
                sql = "SELECT name FROM mdl_quiz where course = " + str(request.POST['context_id'])
                cursor.execute(sql)
                for row in cursor:
                    quizNames.append(row['name'])

            # print(tests)
            numberTests = []
            i = 1
            for test in tests:
                numberTests.append(i)
                i += 1


        finally:
            connection.close()
        return render(
            request,
            'bridge/tests.html',
            context={"contextId": request.POST['context_id'], "quizNames": quizNames,
                     "nameCourse": request.POST['context_title'],
                     "tests": len(numberTests)}
        )
    return HttpResponse('')


def getCategorisWithIdFromIds(ids):
    categoriesWithId = []
    connection = pymysql.connect(host='127.0.0.1',
                                 user='bn_moodle',
                                 password='',
                                 db='bitnami_moodle',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            categories = set()
            print(ids)
            for id in ids:
                sql = "SELECT category FROM mdl_question where id = " + str(id)  # ПОМЕНЯТЬ
                cursor.execute(sql)
                for row in cursor:
                    categories.add(row['category'])
            categories = sorted(categories)
            print(categories)
            for categ in categories:
                categoriesWithId.append([])
                categoriesWithId[len(categoriesWithId) - 1].append(categ)
                categoriesWithId[len(categoriesWithId) - 1].append([])
                sql = "SELECT id FROM mdl_question where category = " + str(categ)  # ПОМЕНЯТЬ
                cursor.execute(sql)
                for row in cursor:
                    categoriesWithId[len(categoriesWithId) - 1][1].append(row['id'])
            print(categoriesWithId)


    finally:
        connection.close()
    return categoriesWithId


def getResultFromCategoryAndIdUser(userId, category):
    grade = -1
    listGgrade = []
    connection = pymysql.connect(host='127.0.0.1',
                                 user='bn_moodle',
                                 password='',
                                 db='bitnami_moodle',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id FROM mdl_question where category = " + str(category)
            cursor.execute(sql)
            setCat = set()
            for row in cursor:
                setCat.add(row['id'])
            for cat in setCat:
                sql = "SELECT * FROM mdl_question_attempt_steps where questionattemptid IN (SELECT id FROM mdl_question_attempts where questionid = " + str(
                    str(cat)) + ") and state <> 'todo' and state <> 'complete' and userid = " + str(userId)
                cursor.execute(sql)
                for string in cursor:
                    value = 0
                    if string['state'] == "gradedright" or string['state'] == "gradedpartial": value = '1'
                    if string['state'] == "gradedwrong" or string['state'] == "gaveup": value = '0'
                    listGgrade.append(value)
    finally:
        connection.close()
    if len(listGgrade) == 0: listGgrade.append("")
    return listGgrade


def getTableFromCategoriesWithIdAndStudent(categoriesWithId, studentList):
    globalTableWithData = []
    connection = pymysql.connect(host='127.0.0.1',
                                 user='bn_moodle',
                                 password='',
                                 db='bitnami_moodle',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            globalTableWithData.append([])
            globalTableWithData[0].append('idStudent')
            for numb in sorted(categoriesWithId):
                globalTableWithData[0].append("id" + str(numb[0]))
            print(tabulate(globalTableWithData, tablefmt="grid"))
            for student in sorted(studentList):
                sql = "SELECT email,firstname,lastname FROM mdl_user where id =" + str(student)
                cursor.execute(sql)
                name = ""
                for row in cursor:
                    name = row['lastname'] + " " + row['firstname'] + " " + row['email']
                globalTableWithData.append([])
                globalTableWithData[len(globalTableWithData) - 1].append(name)
                for cat in sorted(categoriesWithId):
                    grade = getResultFromCategoryAndIdUser(student, cat[0])
                    globalTableWithData[len(globalTableWithData) - 1].append(grade[0])

    finally:
        connection.close()
    return globalTableWithData


def getTaskNameForId(taskId):
    connection = pymysql.connect(host='127.0.0.1',
                                 user='bn_moodle',
                                 password='',
                                 db='bitnami_moodle',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            name = ""
            categoryName = ""
            categoryId = 0
            sql = "SELECT name,category FROM mdl_question where id = " + str(taskId)
            cursor.execute(sql)
            for row in cursor:
                name = row['name']
                categoryId = row['category']
            sql = "SELECT name FROM mdl_question_categories where id = " + str(categoryId)
            cursor.execute(sql)
            for row in cursor:
                categoryName = row['name']
            fullName = str(categoryName) + "(" + str(name) + ")"

    finally:
        connection.close()
    return fullName


def getCategoryNameForId(categoryId):
    connection = pymysql.connect(host='127.0.0.1',
                                 user='bn_moodle',
                                 password='',
                                 db='bitnami_moodle',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            categoryName = ""
            sql = "SELECT name FROM mdl_question_categories where id = " + str(categoryId)
            cursor.execute(sql)
            for row in cursor:
                categoryName = row['name']
    finally:
        connection.close()
    return categoryName


@csrf_exempt
def provider(request):
    studentBrain = []
    pictureGrapfic = []
    pictureGrapficForAllTest = []
    hardTask = []
    hardTaskForAllTest = []
    Xsquares = []
    XsquaresForAllTest = []
    pictureGrapficWithPoint = []
    pictureGrapficWithPointForAllTest = []
    if request.method == 'POST':
        # print(request.POST)
        testNumber = request.POST['testnumber']
        connection = pymysql.connect(host='127.0.0.1',
                                     user='bn_moodle',
                                     password='',
                                     db='bitnami_moodle',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM mdl_question_categories where contextid = " + str(courseNumber)  # ПОМЕНЯТЬ
                cursor.execute(sql)
                # print()
                idCategory = []  # получаем idCategory нашего КУРСА
                for row in cursor:
                    idCategory.append(row['id'])
                # print(idCategory)

                # ищем задания из нашего курса
                taskId = []
                taskIdWithStudents = []
                for id in idCategory:
                    sql = "SELECT * FROM mdl_question where category = " + str(id)
                    cursor.execute(sql)
                    for row in cursor:
                        taskId.append([])
                        taskIdWithStudents.append([])
                        taskId[len(taskId) - 1].append(row['id'])
                        taskIdWithStudents[len(taskId) - 1].append(row['id'])
                        # print(row)  # нащи задания
                # print(taskId)
                # print()
                questionusageid = []
                for id in taskId:
                    sql = "SELECT * FROM mdl_question_attempts where questionid = " + str(id[0])
                    cursor.execute(sql)
                    id.append([])
                    for row in cursor:
                        id[1].append(row['questionusageid'])  # в taskid это будет элемент под индексом 1
                        questionusageid.append(row['questionusageid'])
                # print(len(taskId))
                forDelet = []
                for id in taskId:
                    if len(id[1]) == 0:
                        forDelet.append(id)
                for dele in forDelet:
                    taskId.remove(dele)
                # print()
                # print(len(taskId))
                # print(questionusageid)
                # print(taskId)
                for id in taskId:
                    quizes = set()
                    for i in id[1]:
                        sql = "SELECT * FROM mdl_question_usages where id = " + str(i)
                        cursor.execute(sql)
                        for row in cursor:  # получение разных квизов
                            quizes.add(row['contextid'])
                    id.append(quizes)
                # print(taskId)
                quizes = set()
                for id in taskId:
                    for i in id[2]:
                        quizes.add(i)
                # print(sorted(quizes))
                tests = []  # задания распределены по тестам.
                for contextid in sorted(quizes):
                    tests.append([])
                    for id in taskId:
                        for i in id[2]:
                            if i == contextid:
                                tests[len(tests) - 1].append(id[0])
                # print("Тесты: " + str(tests))
                # print(taskIdWithStudents)  # в каждом списке первая цифра будет айди задания п соледующие айди студентов, кьл его решил
                for number in taskIdWithStudents:
                    sql = "SELECT * FROM mdl_question_attempt_steps where questionattemptid IN (SELECT id FROM mdl_question_attempts where questionid = " + str(
                        number[0]) + ") and state <> 'todo' and state <> 'complete'"
                    cursor.execute(sql)
                    for row in cursor:  # получение разных квизов
                        # print(row)
                        number.append(str(row['userid']) + " " + row['state'])
                    # print()
                # print(taskIdWithStudents)

                k = 1
                for test in tests:
                    if not int(k) == int(testNumber):
                        # print("tuuuuuuuuut")
                        k += 1
                        continue
                    k += 1
                    globalTableWithData = []
                    globalTableWithData.append([])
                    globalTableWithData[0].append('idStudent')
                    for numb in sorted(test):
                        globalTableWithData[0].append("id" + str(numb))
                    # print(tabulate(globalTableWithData, tablefmt="grid"))
                    students = set()
                    print(test)
                    sql = "SELECT id FROM mdl_quiz where course = " + str(request.POST['context_id'])
                    cursor.execute(sql)
                    i = 1
                    quizId = 0
                    for row in cursor:
                        if int(i) == int(testNumber):
                            quizId = row['id']
                            break
                        i += 1
                    print(quizId)

                    # for numb in test:
                    #     for stud in taskIdWithStudents:
                    #         if not numb == stud[0]: continue
                    #         for part in stud:
                    #             if numb == part: continue
                    #             students.add(int(str(part).split(" ")[0]))
                    sql = "SELECT userid FROM mdl_quiz_attempts where quiz = " + str(quizId)
                    cursor.execute(sql)
                    for row in cursor:
                        students.add(row['userid'])
                    # print(sorted(students))
                    quizName = ""
                    sql = "SELECT name FROM mdl_quiz where id = " + str(quizId)
                    cursor.execute(sql)
                    for row in cursor:
                        quizName = row['name']

                    for student in sorted(students):
                        sql = "SELECT email,firstname,lastname FROM mdl_user where id =" + str(student)
                        cursor.execute(sql)
                        name = ""
                        for row in cursor:
                            name = row['lastname'] + " " + row['firstname'] + " " + row['email']
                        globalTableWithData.append([])
                        globalTableWithData[len(globalTableWithData) - 1].append(name)
                    # print(tabulate(globalTableWithData, tablefmt="grid"))
                    i = 1
                    for numb in sorted(test):  # идем по каждому заданию в тесте
                        studAdd = set()
                        for row in globalTableWithData:
                            if row[0] == "idStudent": continue
                            row.append("")
                        for stud in taskIdWithStudents:  # пробегаем по все id заданий
                            if not numb == stud[0]: continue
                            # print(stud)
                            for part in stud:
                                if numb == part: continue
                                sql = "SELECT email,firstname,lastname FROM mdl_user where id =" + str(part).split(" ")[
                                    0]
                                cursor.execute(sql)
                                name = ""
                                for row in cursor:
                                    name = row['lastname'] + " " + row['firstname'] + " " + row['email']
                                studAdd.add(name)
                                for row in globalTableWithData:
                                    if not row[0] == name: continue
                                    if row[0] == name:
                                        value = 0
                                        if str(part).split(" ")[1] == "gradedright" or str(part).split(" ")[
                                            1] == "gradedpartial": value = '1'
                                        if str(part).split(" ")[1] == "gradedwrong" or str(part).split(" ")[
                                            1] == "gaveup": value = '0'
                                        row[i] = value
                        i += 1
                    # print(tabulate(globalTableWithData, tablefmt="grid"))
                    # print()
                    # i = 0
                    # for row in globalTableWithData:
                    #     if i == 0:
                    #         i += 1
                    #         continue
                    #     all = 0
                    #     for part in row:
                    #         if str(part) == "1" or str(part) == "0": all += 1
                    #     print(all)
                    #     i += 1

                    studentsName = []
                    studentsNameForAllTest = []
                    idTask = []
                    idTaskForAllTest = []
                    solve_tests(globalTableWithData, hardTask, studentBrain, pictureGrapfic, idTask, studentsName)
                    for student in studentBrain:
                        if Decimal(student[2]).is_infinite(): student[2] = math.inf
                    # print(tabulate(globalTableWithData, tablefmt="grid"))

                    calibr(globalTableWithData, pictureGrapficWithPoint, Xsquares)
                    print(studentBrain)
                    i = 0
                    # print(pictureGrapfic)
                    print(len(taskIdWithStudents))
                    print(len(test))
                    print(len(studentBrain))
                    print(len(pictureGrapfic))
                    print(sorted(Xsquares))
                    Xsquares = sorted(Xsquares)
                    Xcrit = 18.5
                    for Xsquare in Xsquares:
                        if Xsquare[0] >= Xcrit:
                            Xsquare.append("Гипотетическая модель Раша НЕ согласуется с опытными данными.")
                        if Xsquare[0] < Xcrit:
                            Xsquare.append("Гипотетическая модель Раша согласуется с опытными данными.")

                    categories = getCategorisWithIdFromIds(test)
                    tableForTest = getTableFromCategoriesWithIdAndStudent(categories, students)
                    # print(tabulate(tableForTest, tablefmt="grid"))
                    solve_testsForAllTest(tableForTest, hardTaskForAllTest, pictureGrapficForAllTest, quizName,
                                          idTaskForAllTest, studentsNameForAllTest)
                    print(tabulate(tableForTest, tablefmt="grid"))
                    calibr(tableForTest, pictureGrapficWithPointForAllTest, XsquaresForAllTest)
                    for Xsquare in XsquaresForAllTest:
                        if Xsquare[0] >= Xcrit:
                            Xsquare.append("Гипотетическая модель Раша НЕ согласуется с опытными данными.")
                        if Xsquare[0] < Xcrit:
                            Xsquare.append("Гипотетическая модель Раша согласуется с опытными данными.")
                    print(studentBrain)
                    # print(Xsquares)
                    for Xsquare in Xsquares:
                        name = getTaskNameForId(str(Xsquare[1]).split('d')[1])
                        Xsquare[1] = name
                    # print(Xsquares)
                    # print(XsquaresForAllTest)
                    for Xsquare in XsquaresForAllTest:
                        name = getCategoryNameForId(str(Xsquare[1]).split('d')[1])
                        Xsquare[1] = name
                    # print(XsquaresForAllTest)
                    for task in hardTask:
                        for id in idTask:
                            if str(task[0]) == str(id[0]):
                                task.append(str(id[3]))
                        name = getTaskNameForId(str(task[0]).split('d')[1])
                        task[0] = name
                    print(hardTaskForAllTest)
                    for task in hardTaskForAllTest:
                        for id in idTaskForAllTest:
                            if str(task[0]) == str(id[0]):
                                task.append(str(id[3]))
                        name = getCategoryNameForId(str(task[0]).split('d')[1])
                        task[0] = name
                    for student in studentBrain:
                        for name in studentsName:
                            if student[0] == name[0]:
                                student.append(str(name[3]))
                    tableTaskIdAndName = []
                    for id in sorted(test):
                        tableTaskIdAndName.append([])
                        tableTaskIdAndName[len(tableTaskIdAndName) - 1].append(id)
                        tableTaskIdAndName[len(tableTaskIdAndName) - 1].append(getTaskNameForId(id))
                    categoriesIds = []
                    for id in categories:
                        categoriesIds.append(id[0])
                    tableCategoryIdAndName = []
                    for id in sorted(categoriesIds):
                        tableCategoryIdAndName.append([])
                        tableCategoryIdAndName[len(tableCategoryIdAndName) - 1].append(id)
                        tableCategoryIdAndName[len(tableCategoryIdAndName) - 1].append(getCategoryNameForId(id))
                    # print(Xsquares)
                    print(studentBrain)
                    print(hardTask)
                    # print(XsquaresForAllTest)

                # for student in taskIdWithStudents:

        finally:
            connection.close()
        return render(
            request,
            'bridge/provider.html',
            context={"Xsquares": Xsquares, "XsquaresForAllTest": XsquaresForAllTest, "studentBrain": studentBrain,
                     "hardTask": hardTask, "hardTaskForAllTest": hardTaskForAllTest,
                     "pictureGrapficWithPointForAllTest": pictureGrapficWithPointForAllTest,
                     "pictureGrapficWithPoint": pictureGrapficWithPoint,
                     "pictureGrapficForAllTest": pictureGrapficForAllTest, "tableTaskIdAndName": tableTaskIdAndName,
                     "tableCategoryIdAndName": tableCategoryIdAndName,
                     "context_title": request.POST['context_title'], "context_id": request.POST['context_id']}
        )
    return HttpResponse('')


def solvePi(Qi, Bi):
    difference = float(Qi) - float(Bi)
    e = math.exp(float(1.7) * float(difference))
    Pi = e / (1 + e)
    # Pi = float('{:.4f}'.format(Pi))
    return Pi


def createGrafics(resultArrBi, name, points=[], people=[], Xsquare=[], x=5, y=3):
    fig = plt.figure(figsize=(x, y))
    plt.title(name, fontsize=17)  # заголовок
    plt.xlabel("Q", fontsize=17)  # ось абсцисс
    plt.ylabel("Pi", fontsize=17)  # ось ординат
    plt.grid(True)
    arrQ = [-5, -4.5, -4, -3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5,
            1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]  # набор Q, которые будут подставляться для расчетов
    for Bi in resultArrBi:  # проходим по всем заданиям теста
        i = 0
        arrP = []
        if Bi[1] == -math.inf:
            Bi[1] = -3
        if Bi[1] == math.inf:
            Bi[1] = 3
        for Q in arrQ:
            arrP.append([])
            arrP[i].append(Q)
            arrP[i].append(solvePi(Q, Bi[1]))
            i += 1
        # print(arrP)
        x = []
        y = []
        for var in arrP:
            x.append(var[0])
            y.append(var[1])

        plt.plot(x, y, label=Bi[0])
        plt.legend(bbox_to_anchor=(1.05, 1.15), loc='upper left')
    i = 0
    X = 0
    for point in points:
        if point == None:
            i += 1
            continue
        if i == 0: x_data = -3.75
        if i == 1: x_data = -1.75
        if i == 2: x_data = -0.75
        if i == 3: x_data = -0.25
        if i == 4: x_data = 0.25
        if i == 5: x_data = 0.75
        if i == 6: x_data = 1.75
        if i == 7: x_data = 3.75
        y_data = [point]
        X += people[i] * (
                (point - solvePi(x_data, resultArrBi[0][1])) ** 2 / (
                solvePi(x_data, resultArrBi[0][1]) * (
                1 / (1 + math.exp(float(1.7) * float(x_data - resultArrBi[0][1]))))))
        plt.scatter(x_data, y_data, c='r')
        i += 1
    Xsquare.append(float('{:.2f}'.format(X)))
    Xsquare.append(name)
    plt.show()
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return data


def calibr(globalTableWithData, pictureGrapficWithPoint, Xsquares):
    nameAndQ = []
    i = 0
    for row in globalTableWithData:
        if row[0] == "idStudent" or row[0] == "Bi0" or row[0] == "Bi": continue
        nameAndQ.append([])
        nameAndQ[i].append(row[len(row) - 1])
        nameAndQ[i].append(row[0])
        nameAndQ[i].append(i + 1)
        i += 1
    print(sorted(nameAndQ))
    # Буду брать от -2.5 до -1 от -1 до -0.5 от -0.5 до 0 от 0 до 0.5 от 0.5 до 1 от 1 до 2.5
    gap_5_25 = []
    gap_25_1 = []
    gap_1_05 = []
    gap_05_0 = []
    gap005 = []
    gap051 = []
    gap125 = []
    gap255 = []
    for pair in nameAndQ:
        if pair[0] < -2.5: gap_5_25.append(pair)
        if -2.5 <= pair[0] < -1: gap_25_1.append(pair)
        if -1 <= pair[0] < -0.5: gap_1_05.append(pair)
        if -0.5 <= pair[0] < 0: gap_05_0.append(pair)
        if 0 <= pair[0] < 0.5: gap005.append(pair)
        if 0.5 <= pair[0] < 1: gap051.append(pair)
        if 1 <= pair[0] < 2.5: gap125.append(pair)
        if 2.5 <= pair[0] < 5: gap255.append(pair)
    print(gap_5_25)
    print(gap_25_1)
    print(gap_1_05)
    print(gap_05_0)
    print(gap005)
    print(gap051)
    print(gap125)
    print(gap255)
    tasks = []
    indexTask = 0
    for task in globalTableWithData[0]:
        if task == "idStudent" or task == "Qi" or task == "Qi0": continue
        tasks.append([])
        tasks[indexTask].append(task)
        tasks[indexTask].append(indexTask + 1)
        tasks[indexTask].append(globalTableWithData[len(globalTableWithData) - 1][indexTask + 1])
        indexTask += 1
    print(tasks)
    print(len(globalTableWithData[0]) - 3)
    for task in tasks:
        one = 0
        zero = 0
        people = []
        result = []
        for gap in gap_5_25:
            if globalTableWithData[gap[2]][task[1]] == "1": one += 1
            if globalTableWithData[gap[2]][task[1]] == "0": zero += 1
        if (one + zero) == 0:
            result.append(None)
            people.append(None)
        else:
            result.append(one / (one + zero))
            people.append(one + zero)
        one = 0
        zero = 0
        for gap in gap_25_1:
            if globalTableWithData[gap[2]][task[1]] == "1": one += 1
            if globalTableWithData[gap[2]][task[1]] == "0": zero += 1
        if (one + zero) == 0:
            result.append(None)
            people.append(None)
        else:
            result.append(one / (one + zero))
            people.append(one + zero)
        one = 0
        zero = 0
        for gap in gap_1_05:
            if globalTableWithData[gap[2]][task[1]] == "1": one += 1
            if globalTableWithData[gap[2]][task[1]] == "0": zero += 1
        if (one + zero) == 0:
            result.append(None)
            people.append(None)
        else:
            result.append(one / (one + zero))
            people.append(one + zero)
        one = 0
        zero = 0
        for gap in gap_05_0:
            if globalTableWithData[gap[2]][task[1]] == "1": one += 1
            if globalTableWithData[gap[2]][task[1]] == "0": zero += 1
        if (one + zero) == 0:
            result.append(None)
            people.append(None)
        else:
            result.append(one / (one + zero))
            people.append(one + zero)
        one = 0
        zero = 0
        for gap in gap005:
            if globalTableWithData[gap[2]][task[1]] == "1": one += 1
            if globalTableWithData[gap[2]][task[1]] == "0": zero += 1
        if (one + zero) == 0:
            result.append(None)
            people.append(None)
        else:
            result.append(one / (one + zero))
            people.append(one + zero)
        one = 0
        zero = 0
        for gap in gap051:
            if globalTableWithData[gap[2]][task[1]] == "1": one += 1
            if globalTableWithData[gap[2]][task[1]] == "0": zero += 1
        if (one + zero) == 0:
            result.append(None)
            people.append(None)
        else:
            result.append(one / (one + zero))
            people.append(one + zero)
        one = 0
        zero = 0
        for gap in gap125:
            if globalTableWithData[gap[2]][task[1]] == "1": one += 1
            if globalTableWithData[gap[2]][task[1]] == "0": zero += 1
        if (one + zero) == 0:
            result.append(None)
            people.append(None)
        else:
            result.append(one / (one + zero))
            people.append(one + zero)
        one = 0
        zero = 0
        for gap in gap255:
            if globalTableWithData[gap[2]][task[1]] == "1": one += 1
            if globalTableWithData[gap[2]][task[1]] == "0": zero += 1
        if (one + zero) == 0:
            result.append(None)
            people.append(None)
        else:
            result.append(one / (one + zero))
            people.append(one + zero)
        result.append(task[0])
        all = 0
        koef = 0
        for res in result:
            if res is None or str(res).__contains__("id"): continue
            all += 1
            koef += res
        print(result)
        print(people)
        # Рисование графиков с точками
        numberLine = 0
        arrForGraph = []
        arrForGraph.append([])
        arrForGraph[0].append(task[0])
        arrForGraph[0].append(task[2])
        name = task[0]
        resultForGraph = []
        for res in result:
            if str(res).__contains__("id"): continue
            resultForGraph.append(res)
        Xsquare = []
        grapfic = createGrafics(arrForGraph, name, resultForGraph, people, Xsquare)
        pictureGrapficWithPoint.append(grapfic)
        Xsquare.append(grapfic)
        # print("Xsquare : " + str(Xsquare))
        Xsquares.append(Xsquare)


def solve_tests(globalTableWithData, hardTask, studentBrain, pictureGrapfic, idTask, studentsName):
    # Находим Bi0
    for id in globalTableWithData[0]:  # Заполняем set idTask названиями id заданий
        if id == 'idStudent':
            continue
        idTask.append([])
        idTask[len(idTask) - 1].append(str(id))
    print(idTask)
    i = 0
    array = []
    resultArr = []
    for val in idTask:  # Проходим по всем id заданий
        all = 0
        one = 0
        zero = 0
        # print(val)
        rows = []
        for k in range(len(globalTableWithData)):  # Проходим по всем студентам, кто решал задания
            if k == 0:  # Первую строку пропускаем, так как там id задания
                continue
            if str(globalTableWithData[k][i + 1]).__contains__("1") or str(globalTableWithData[k][i + 1]).__contains__(
                    # Тут отсееваем None и добавляем только то, что содержит в себе либо 0 либо 1
                    "0"):
                rows.append(str(globalTableWithData[k][i + 1]))
        # print(rows)
        for row in rows:  # Определяем количество нулей и единиц
            if row.__contains__("1"):
                one += 1
            if row.__contains__("0"):
                zero += 1
            all += 1
        # print(all)
        array.append([])
        array[i].append(one)
        array[i].append(zero)
        array[i].append(all)
        array[i].append(one / all)
        val.append(one / all)
        array[i].append(1 - array[i][3])
        val.append(1 - (one / all))
        if not array[i][3] == 0.0:
            d = Decimal(array[i][4] / array[i][3])  # Высчитываем показатель Bi0
        if array[i][3] == 0.0:
            d = Decimal(math.inf)
        resultArr.append([])  # Заполняем список результатов
        resultArr[i].append(val[0])
        resultArr[i].append(float('{:.3f}'.format(float(d.ln()))))
        i += 1

    # Вставка Bi0 в таблицу со значениями последний строкой
    globalTableWithData.append([])
    globalTableWithData[len(globalTableWithData) - 1].append("Bi0")
    for result in resultArr:
        globalTableWithData[len(globalTableWithData) - 1].append(result[1])
    print(resultArr)

    resultArrBi = resultArr
    resultArrSize = len(resultArr)
    Bi0Midle = 0
    for res in resultArr:
        if res[1] == Decimal(math.inf):
            resultArrSize -= 1
            continue
        if res[1] == -Decimal(math.inf):
            resultArrSize -= 1
            continue
        Bi0Midle += res[1]
    Bi0Midle /= resultArrSize
    print("Bi0Midle = " + str(Bi0Midle))

    sumBi0Square = 0
    for res in resultArr:
        if res[1] == Decimal(math.inf):
            continue
        if res[1] == -Decimal(math.inf):
            continue
        sumBi0Square += res[1] ** 2
    print("sumBi0Square = " + str(sumBi0Square))
    delitel = resultArrSize - 1
    if delitel == 0: delitel = 0.00001
    SB = (sumBi0Square - resultArrSize * Bi0Midle ** 2) / delitel
    print("SB = " + str(SB))

    # Находим Qi0
    array = []
    resultArr = []
    i = 0
    for k in range(len(globalTableWithData)):
        if k == 0 or k == len(globalTableWithData) - 1: continue
        studentsName.append([])
        studentsName[len(studentsName) - 1].append(globalTableWithData[k][0])
    print(studentsName)

    for name in studentsName:
        all = 0
        one = 0
        zero = 0
        rows = []
        for index in range(len(globalTableWithData[0])):
            if i == len(globalTableWithData) - 1: continue
            rows.append(globalTableWithData[i + 1][index])
        for row in str(rows).split(","):
            if row.__contains__("1"):
                one += 1
            if row.__contains__("0"):
                zero += 1
        all = one + zero
        array.append([])
        array[i].append(one)
        array[i].append(zero)
        array[i].append(all)
        if not all == 0:
            name.append(one / all)
            name.append(1 - (one / all))
        else:
            name.append(Decimal(math.inf))
            name.append(Decimal(math.inf))
        if not all == 0:
            array[i].append(one / all)
            array[i].append(1 - array[i][3])
            if not array[i][4] == 0.0:
                print(array[i])
                d = Decimal(array[i][3] / array[i][4])
            if array[i][4] == 0.0:
                d = Decimal(math.inf)
        else:
            d = Decimal(math.inf)  # Человек не писал тест
        resultArr.append([])
        resultArr[i].append(name[0])
        resultArr[i].append(float('{:.3f}'.format(float(d.ln()))))
        i += 1

    globalTableWithData[0].append("Qi0")
    for indexName in range(len(resultArr)):
        globalTableWithData[indexName + 1].append(resultArr[indexName][1])

    resultArrQi = resultArr
    resultArrSize = len(resultArr)
    Qi0Midle = 0
    for res in resultArr:
        if res[1] == Decimal(math.inf):
            resultArrSize -= 1
            continue
        if res[1] == -Decimal(math.inf):
            resultArrSize -= 1
            continue
        Qi0Midle += res[1]
    Qi0Midle /= resultArrSize
    print("Qi0Midle = " + str(Qi0Midle))

    sumQi0Square = 0
    for res in resultArr:
        if res[1] == Decimal(math.inf):
            continue
        if res[1] == -Decimal(math.inf):
            continue
        sumQi0Square += res[1] ** 2
    print("sumQi0Square = " + str(sumQi0Square))

    SQ = (sumQi0Square - resultArrSize * Qi0Midle ** 2) / (resultArrSize - 1)
    print("SQ = " + str(SQ))

    AB = math.sqrt((1 + SQ / 2.89) / (1 - SQ * SB / 8.35))
    print("AB = " + str(AB))

    AQ = math.sqrt((1 + SB / 2.89) / (1 - SQ * SB / 8.35))
    print("AQ = " + str(AQ))

    for res in resultArrBi:
        if res[1] == Decimal(math.inf):
            res.append(Decimal(math.inf))
            continue
        if res[1] == -Decimal(math.inf):
            res.append(-Decimal(math.inf))
            continue
        res.append(float('{:.3f}'.format(AB * res[1] + Qi0Midle)))
    # print(resultArrBi)

    for res in resultArrQi:
        if res[1] == Decimal(math.inf):
            res.append(Decimal(math.inf))
            continue
        if res[1] == -Decimal(math.inf):
            res.append(-Decimal(math.inf))
            continue
        res.append(float('{:.3f}'.format(AQ * res[1] + Bi0Midle)))
    # print(resultArrQi)

    globalTableWithData[0].append("Qi")
    for indexResultArrQi in range(len(resultArrQi)):
        globalTableWithData[indexResultArrQi + 1].append(resultArrQi[indexResultArrQi][2])

    globalTableWithData.append([])
    globalTableWithData[len(globalTableWithData) - 1].append("Bi")
    for result in resultArrBi:
        globalTableWithData[len(globalTableWithData) - 1].append(result[2])
    print(resultArr)
    for arr in resultArr:
        studentBrain.append(arr)
    for arr in resultArrBi:
        hardTask.append([])
        hardTask[len(hardTask) - 1].append(str(arr[0]))
        hardTask[len(hardTask) - 1].append(str(arr[2]))

    for task in idTask:
        delitel = float('{:.3f}'.format(float(math.sqrt(len(studentsName) * task[1] * task[2]))))
        if delitel == 0:
            standartMistake = Decimal(math.inf)
            task.append(standartMistake)
            continue
        standartMistake = float('{:.3f}'.format(float(AB / delitel)))
        task.append(standartMistake)

    for student in studentsName:
        delitel = float('{:.3f}'.format(float(math.sqrt(len(idTask) * student[1] * student[2]))))
        if delitel == 0:
            standartMistake = Decimal(math.inf)
            student.append(standartMistake)
            continue
        standartMistake = float('{:.3f}'.format(float(AQ / delitel)))
        student.append(standartMistake)
    # Создание графиков
    # numberLine = 0
    # for line in globalTableWithData:
    #     if numberLine == 0:
    #         numberLine += 1
    #         continue
    #     arrForGraph = []
    #     name = line[0]
    #     colmn = 0
    #     for qi in resultArrQi:
    #         if name == qi[0]:
    #             name = str(name).split(" ")[0] + " " + str(name).split(" ")[1] + " (Qi = " + str(qi[2]) + ")"
    #     i = 0
    #     for var in line:
    #         if colmn >= len(globalTableWithData[0]): break
    #         if var == '0' or var == '1':
    #             id = globalTableWithData[0][colmn]
    #             for bi in resultArrBi:
    #                 if id == bi[0]:
    #                     arrForGraph.append([])
    #                     arrForGraph[i].append(id)
    #                     arrForGraph[i].append(bi[2])
    #                     i += 1
    #         colmn += 1
    #     numberLine += 1
    #     if not len(arrForGraph) == 0:
    #         pictureGrapfic.append(createGrafics(arrForGraph, name))


def solve_testsForAllTest(globalTableWithData, hardTask, pictureGrapfic, quizName, idTask, studentsName):
    # Находим Bi0
    for id in globalTableWithData[0]:  # Заполняем set idTask названиями id заданий
        if id == 'idStudent':
            continue
        idTask.append([])
        idTask[len(idTask) - 1].append(str(id))
    print(idTask)
    print(idTask)
    i = 0
    array = []
    resultArr = []
    for val in idTask:  # Проходим по всем id заданий
        all = 0
        one = 0
        zero = 0
        # print(val)
        rows = []
        for k in range(len(globalTableWithData)):  # Проходим по всем студентам, кто решал задания
            if k == 0:  # Первую строку пропускаем, так как там id задания
                continue
            if str(globalTableWithData[k][i + 1]).__contains__("1") or str(globalTableWithData[k][i + 1]).__contains__(
                    # Тут отсееваем None и добавляем только то, что содержит в себе либо 0 либо 1
                    "0"):
                rows.append(str(globalTableWithData[k][i + 1]))
        # print(rows)
        for row in rows:  # Определяем количество нулей и единиц
            if row.__contains__("1"):
                one += 1
            if row.__contains__("0"):
                zero += 1
            all += 1
        # print(all)
        array.append([])
        array[i].append(one)
        array[i].append(zero)
        array[i].append(all)
        array[i].append(one / all)
        array[i].append(1 - array[i][3])
        val.append(one / all)
        val.append(1 - (one / all))
        if not array[i][3] == 0.0:
            d = Decimal(array[i][4] / array[i][3])  # Высчитываем показатель Bi0
        if array[i][3] == 0.0:
            d = Decimal(math.inf)
        resultArr.append([])  # Заполняем список результатов
        resultArr[i].append(val[0])
        resultArr[i].append(float('{:.3f}'.format(float(d.ln()))))
        i += 1

    # Вставка Bi0 в таблицу со значениями последний строкой
    globalTableWithData.append([])
    globalTableWithData[len(globalTableWithData) - 1].append("Bi0")
    for result in resultArr:
        globalTableWithData[len(globalTableWithData) - 1].append(result[1])
    print(resultArr)

    resultArrBi = resultArr
    resultArrSize = len(resultArr)
    Bi0Midle = 0
    for res in resultArr:
        if res[1] == Decimal(math.inf):
            resultArrSize -= 1
            continue
        if res[1] == -Decimal(math.inf):
            resultArrSize -= 1
            continue
        Bi0Midle += res[1]
    Bi0Midle /= resultArrSize
    print("Bi0Midle = " + str(Bi0Midle))

    sumBi0Square = 0
    for res in resultArr:
        if res[1] == Decimal(math.inf):
            continue
        if res[1] == -Decimal(math.inf):
            continue
        sumBi0Square += res[1] ** 2
    print("sumBi0Square = " + str(sumBi0Square))
    delitel = resultArrSize - 1
    if delitel == 0: delitel = 0.00001
    SB = (sumBi0Square - resultArrSize * Bi0Midle ** 2) / delitel
    print("SB = " + str(SB))

    # Находим Qi0
    array = []
    resultArr = []
    i = 0
    for k in range(len(globalTableWithData)):
        if k == 0 or k == len(globalTableWithData) - 1: continue
        studentsName.append([])
        studentsName[len(studentsName) - 1].append(globalTableWithData[k][0])
    print(studentsName)

    for name in studentsName:
        all = 0
        one = 0
        zero = 0
        rows = []
        for index in range(len(globalTableWithData[0])):
            if i == len(globalTableWithData) - 1: continue
            rows.append(globalTableWithData[i + 1][index])
        for row in str(rows).split(","):
            if row.__contains__("1"):
                one += 1
            if row.__contains__("0"):
                zero += 1
        all = one + zero
        array.append([])
        array[i].append(one)
        array[i].append(zero)
        array[i].append(all)
        if not all == 0:
            name.append(one / all)
            name.append(1 - (one / all))
        else:
            name.append(Decimal(math.inf))
            name.append(Decimal(math.inf))
        if not all == 0:
            array[i].append(one / all)
            array[i].append(1 - array[i][3])
            if not array[i][4] == 0.0:
                print(array[i])
                d = Decimal(array[i][3] / array[i][4])
            if array[i][4] == 0.0:
                d = Decimal(math.inf)
        else:
            d = Decimal(math.inf)  # Человек не писал тест
        resultArr.append([])
        resultArr[i].append(name[0])
        resultArr[i].append(float('{:.3f}'.format(float(d.ln()))))
        i += 1

    globalTableWithData[0].append("Qi0")
    for indexName in range(len(resultArr)):
        globalTableWithData[indexName + 1].append(resultArr[indexName][1])

    resultArrQi = resultArr
    resultArrSize = len(resultArr)
    Qi0Midle = 0
    for res in resultArr:
        if res[1] == Decimal(math.inf):
            resultArrSize -= 1
            continue
        if res[1] == -Decimal(math.inf):
            resultArrSize -= 1
            continue
        Qi0Midle += res[1]
    Qi0Midle /= resultArrSize
    print("Qi0Midle = " + str(Qi0Midle))

    sumQi0Square = 0
    for res in resultArr:
        if res[1] == Decimal(math.inf):
            continue
        if res[1] == -Decimal(math.inf):
            continue
        sumQi0Square += res[1] ** 2
    print("sumQi0Square = " + str(sumQi0Square))

    SQ = (sumQi0Square - resultArrSize * Qi0Midle ** 2) / (resultArrSize - 1)
    print("SQ = " + str(SQ))

    AB = math.sqrt((1 + SQ / 2.89) / (1 - SQ * SB / 8.35))
    print("AB = " + str(AB))

    AQ = math.sqrt((1 + SB / 2.89) / (1 - SQ * SB / 8.35))
    print("AQ = " + str(AQ))

    for res in resultArrBi:
        if res[1] == Decimal(math.inf):
            res.append(Decimal(math.inf))
            continue
        if res[1] == -Decimal(math.inf):
            res.append(-Decimal(math.inf))
            continue
        res.append(float('{:.3f}'.format(AB * res[1] + Qi0Midle)))
    # print(resultArrBi)

    for res in resultArrQi:
        if res[1] == Decimal(math.inf):
            res.append(Decimal(math.inf))
            continue
        if res[1] == -Decimal(math.inf):
            res.append(-Decimal(math.inf))
            continue
        res.append(float('{:.3f}'.format(AQ * res[1] + Bi0Midle)))
    # print(resultArrQi)

    globalTableWithData[0].append("Qi")
    for indexResultArrQi in range(len(resultArrQi)):
        globalTableWithData[indexResultArrQi + 1].append(resultArrQi[indexResultArrQi][2])

    globalTableWithData.append([])
    globalTableWithData[len(globalTableWithData) - 1].append("Bi")
    for result in resultArrBi:
        globalTableWithData[len(globalTableWithData) - 1].append(result[2])
    print(resultArr)
    for arr in resultArrBi:
        hardTask.append([])
        hardTask[len(hardTask) - 1].append(str(arr[0]))
        hardTask[len(hardTask) - 1].append(str(arr[2]))
    print(hardTask)

    for task in idTask:
        delitel = float('{:.3f}'.format(float(math.sqrt(len(studentsName) * task[1] * task[2]))))
        if delitel == 0:
            standartMistake = Decimal(math.inf)
            task.append(standartMistake)
            continue
        standartMistake = float('{:.3f}'.format(float(AB / delitel)))
        task.append(standartMistake)

    for student in studentsName:
        delitel = float('{:.3f}'.format(float(math.sqrt(len(idTask) * student[1] * student[2]))))
        if delitel == 0:
            standartMistake = Decimal(math.inf)
            student.append(standartMistake)
            continue
        standartMistake = float('{:.3f}'.format(float(AQ / delitel)))
        student.append(standartMistake)

    # Создание графиков
    numberLine = 0
    arrForGraph = []
    name = quizName
    colmn = 0
    i = 1
    for string in globalTableWithData[0]:
        if string == "idStudent": continue
        if string == "Qi0": break
        arrForGraph.append([])
        arrForGraph[len(arrForGraph) - 1].append(globalTableWithData[0][i])
        arrForGraph[len(arrForGraph) - 1].append(globalTableWithData[len(globalTableWithData) - 1][i])
        i += 1

    if not len(arrForGraph) == 0:
        pictureGrapfic.append(createGrafics(arrForGraph, name, [], [], [], 7, 6))
