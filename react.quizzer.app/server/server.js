const compareVersions = require('compare-versions')
const express = require('express')
const moment = require('moment')
const { v4: uuidv4 } = require('uuid');
const app = express()
app.use(express.json());
const port = 4000
const fs = require('fs')

// https://www.sqlite.org/datatype3.html
const boolTrue = 1
const boolFalse = 0

//var sqlite3 = require('sqlite3').verbose()
//var db = new sqlite3.Database(':memory:')
//var db = new sqlite3.Database("./server/database/quizzer.db")
var sqlite = require("better-sqlite3")
var db = new sqlite("./server/database/quizzer.db")

db.exec('CREATE TABLE IF NOT EXISTS courses(name text)');
db.exec('CREATE TABLE IF NOT EXISTS sessions(coursename text, sessionid text, started text, finished text, qidsjson text, PRIMARY KEY (sessionid))');
db.exec('CREATE TABLE IF NOT EXISTS scores(datetime text, coursename text, sessionid text, score real)');
db.exec('CREATE TABLE IF NOT EXISTS answers(datetime text, sessionid text, coursename text, questionid text, answer text, choiceindex integer, correct bool, PRIMARY KEY (sessionid, coursename, questionid))');

let userSessions = [];
let resultsCache = {};

/*****************************************************
 * FUNCTION: strip the file extension from a filename
*****************************************************/
function removeFileExtension(filename) {
    if ( ! filename.includes('.json') ) { 
        return filename
    }
    const li = filename.lastIndexOf('.');
    const newfn = filename.substr(0, li);
    return newfn
};

/*****************************************************
 * FUNCTION: is a question a multiple-choice question?
*****************************************************/
function fileHasChoices(courseName, filename) {
    const rfilename = 'server/data/courses/' + courseName + '/' + removeFileExtension(filename) + '.json'
    let filedata = fs.readFileSync(rfilename);
    let jData = JSON.parse(filedata);
    if ( jData.choices.length === 0 ) {
        return false
    }
    return true
};

/*****************************************************
 * FUNCTION: is the fill-in-the-blank answer an int?
*****************************************************/
function fileHasIntegerInputAnswer(courseName, filename) {
    const rfilename = 'server/data/courses/' + courseName + '/' + removeFileExtension(filename) + '.json'
    let filedata = fs.readFileSync(rfilename);
    let jData = JSON.parse(filedata);

    if ( jData.choices.length !== 0 ) {
        return false
    }

    if ( ! parseInt(jData.answer) ) {
        return false
    }

    return true
};

/*****************************************************
 * FUNCTION: int or fraction or power?
*****************************************************/
function fileHasSafeAnswer(courseName, filename) {
    const rfilename = 'server/data/courses/' + courseName + '/' + removeFileExtension(filename) + '.json'
    let filedata = fs.readFileSync(rfilename);
    let jData = JSON.parse(filedata);

    let valid = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789^/'.split('')

    let answer = jData.answer
    if ( answer === null || answer === undefined ) {
        return false
    }
    for (let i=0; i<answer.length; i++) {
        if (! valid.includes(answer.charAt(i))) {
            return false
        }
    }

    return true
};

/*****************************************************
 * FUNCTION: int or fraction or power?
*****************************************************/
function fileIsEnabled(courseName, filename) {
    const rfilename = 'server/data/courses/' + courseName + '/' + removeFileExtension(filename) + '.json'
    let filedata = fs.readFileSync(rfilename);
    let jData = JSON.parse(filedata);

    let enabled = jData.enabled
    if ( enabled === false ) {
        return false
    }

    return true
};

/*****************************************************
 * FUNCTION: get question data
*****************************************************/
function getQuestionData(courseName, questionid) {

    const filename = 'server/data/courses/' + courseName + '/' + questionid + '.json'

    let filedata = fs.readFileSync(filename);
    let jData = JSON.parse(filedata);

    return jData;
};

/*****************************************************
 * FUNCTION: get course statistics
*****************************************************/
function getCourseStatistics(courseName) {
    const cacheKey = courseName + '_stats'

    if ( resultsCache.hasOwnProperty(cacheKey) && resultsCache[cacheKey] !== null ) {
        console.log('using cached result for ' + cacheKey);
        return resultsCache[cacheKey]
    }

    let questionList = [...coursesFiles[courseName]]
    questionList.sort(compareVersions);

    let questionStats = {
        coursename: courseName,
        total: questionList.length,
        answered: 0,
        unanswered: 0,
        questionlist: questionList,
        questions: {},
        score_history: [],
        sessionids: []
    };
    for (let i=0; i<questionList.length; i++) {
        questionStats.questions[questionList[i]] = {
            coursename: courseName,
            questionid: questionList[i],
            total: 0,
            correct: 0,
            incorrect: 0
        }
    }

    let sessionIDs = []
    let sessionInfo = {}
    let answered = []
    let unanswered = [...questionList]

    rows = db.prepare(
        `SELECT * FROM answers WHERE coursename='${courseName}'`
    ).all()
    
    let sessionIndex = 0
    rows.forEach((row, row_index) => {
        //console.log(row)

        if (!answered.includes(row.questionid)) {
            answered.push(row.questionid)
        }

        if (!sessionIDs.includes(row.sessionid)) {
            sessionIndex += 1
            sessionIDs.push(row.sessionid)
            sessionInfo[row.sessionid] = {
                sessionid: row.sessionid,
                date: row.datetime,
                label: sessionIndex,
                text: sessionIndex,
                correct: 0,
                incorrect: 0,
                score: 0,
                y: 0
            }
        }

        // get the section for display on the coursepage datatable ...
        const qData = getQuestionData(courseName, row.questionid)
        questionStats.questions[row.questionid].section = qData.section

        questionStats.questions[row.questionid].total += 1
        if (row.correct === boolTrue) {
            questionStats.questions[row.questionid].correct += 1
            sessionInfo[row.sessionid]['correct'] += 1
        } else {
            questionStats.questions[row.questionid].incorrect += 1
            sessionInfo[row.sessionid]['incorrect'] += 1
        }
    })

    // get the section for display on the coursepage datatable ...
    questionList.forEach((questionid, qid) => {
        if ( questionStats.questions[questionid].section === null ||  questionStats.questions[questionid].section === undefined ) {
            const qData = getQuestionData(courseName, questionid)
            questionStats.questions[questionid].section = qData.section
        }
    });

    questionStats.answered = answered.length;
    questionStats.unanswered = unanswered.length;
    questionStats.sessionids = sessionIDs;

    sessionIDs.forEach(sessionID => {
        console.log(sessionID);
        rows = db.prepare(
            `SELECT * FROM sessions WHERE sessionid='${sessionID}'`
        ).all()
        const thisSessionData = rows[0]
        //let thisSessionQuestionIds = []
        //let thisTotalQuestions = 1
        if ( thisSessionData !== undefined ) {
            const thisSessionQuestionIds = JSON.parse(thisSessionData.qidsjson)
            const thisTotalQuestions = thisSessionQuestionIds.length
            sessionInfo[sessionID].date = thisSessionData.started
            sessionInfo[sessionID].total = thisTotalQuestions
            sessionInfo[sessionID].score = (sessionInfo[sessionID].correct / thisTotalQuestions) * 100
            sessionInfo[sessionID].y = (sessionInfo[sessionID].correct / thisTotalQuestions) * 100
            sessionInfo[sessionID].value = (sessionInfo[sessionID].correct / thisTotalQuestions) * 100
        } else {
            delete sessionInfo[sessionID]
        }
    })

    console.log(sessionInfo)
    console.log(Object.values(sessionInfo))
    questionStats.score_history = Object.values(sessionInfo)
    questionStats.session_info = sessionInfo

    resultsCache[cacheKey] = questionStats
    return questionStats
};


/*****************************************************
 * CONST: hash of courses and their questions
*****************************************************/
const courseList = fs.readdirSync('server/data/courses')
console.log(courseList)
let coursesFiles = {};
for (let i=0; i<courseList.length; i++) {
    let courseFileList = fs.readdirSync('server/data/courses/' + courseList[i])
    courseFileList = courseFileList.filter(function(value, indx, arr){
        return value.includes('.json')
    })
    let courseQuestionList = courseFileList.map((filename) => {
        return removeFileExtension(filename);
    })

    /*
    if ( courseList[i] === 'C960_discrete_math_II' ) {
        // clear out non-multiplechoice questions if requested ...
        filtered = courseQuestionList.filter(function(value, indx, arr){
            return (fileHasChoices(courseList[i], value) || fileHasIntegerInputAnswer(courseList[i], value)  || fileHasSafeAnswer(courseList[i], value));
        });
        courseQuestionList = filtered
        console.log('after filters: ', courseQuestionList.length)
    }
    */

    if ( courseList[i] === 'C960_discrete_math_II' ) {
        filtered = courseQuestionList.filter(function(value, indx, arr){
            return fileIsEnabled(courseList[i], value);
        });
    } 

    coursesFiles[courseList[i]] = courseQuestionList
    console.log('after filters: ', coursesFiles[courseList[i]].length)
}

app.get('/api/courses', (req, res) => res.json(courseList))
app.get('/api/courses/:courseName', (req, res) => res.json(req.params))

/*****************************************************
 * WEB: get course question images
*****************************************************/
app.get('/images/:courseName/:imageName', async function (req, res) {
    let fileName = 'data/courses/' + req.params.courseName
    fileName += '/images/'
    fileName += req.params.imageName
    console.log(fileName)
    res.sendFile(fileName, { root: __dirname });
});

/*****************************************************
 * API: return a list of questions for course
*****************************************************/
app.get('/api/courses/:courseName/questions', function (req, res) {
    console.log(req.params)
    let questionList = [...coursesFiles[req.params.courseName]]
    questionList.sort(compareVersions);
    return res.json(questionList)
});

/*****************************************************
 * API: return question data and prev+next question
*****************************************************/
app.get('/api/courses/:courseName/questions/:questionID', function (req, res) {

    // FIXME: return null data for null filenames
    if (req.params.questionID === undefined || req.params.questionID === "undefined") {
        return res.json({
            'qid': req.params.questionID,
            'next': null,
            'previous': null,
            'filename': null,
        })

    }

    const filename = 'server/data/courses/' + req.params.courseName + '/' + req.params.questionID + '.json'
    console.log(filename)

    let filedata = fs.readFileSync(filename);
    let jData = JSON.parse(filedata);

    let previousQ = null;
    let nextQ = null;
    const totalQs = coursesFiles[req.params.courseName].length;

    for (let i=0; i<totalQs; i++) {
        //console.log(req.params.questionID, coursesFiles[req.params.courseName][i])
        if (coursesFiles[req.params.courseName][i] === req.params.questionID) {
            if ( i < (totalQs) ) {
                if ( coursesFiles[req.params.courseName][i+1] !== undefined ) {
                    nextQ = '/courses/' + req.params.courseName + 
                        '/questions/' + coursesFiles[req.params.courseName][i+1]
                    //console.log('nextq', nextQ)
                }
            }
            if ( i > 0 ) {
                previousQ = '/courses/' + req.params.courseName + 
                    '/questions/' + coursesFiles[req.params.courseName][i-1]
                //console.log('prevq', previousQ)
            }
        }
    }

    return res.json({
        'qid': req.params.questionID,
        'next': nextQ,
        'previous': previousQ,
        'filename': filename,
        ...jData
    })
});

/*****************************************************
 * API: get a set of quiz questions
*****************************************************/
app.get('/api/quiz/:courseName', async function (req, res) {

    console.log('------------------------------------------')
    console.log(req.params)
    const courseName = req.params.courseName
    console.log(req.query)

    const searchSectionString = req.query.search_section
    console.log(searchSectionString)
    const byUnanswered = req.query.unanswered
    console.log(byUnanswered)
    const byIncorrect = req.query.incorrect
    console.log(byIncorrect)

    let qCount = req.query.count
    if (qCount === undefined || qCount === null) {
        qCount = "10"
    }
    qCount = parseInt(qCount)

    console.log('#### qCount', qCount)

    let questionList = [...coursesFiles[req.params.courseName]]
    multiplechoice = true;

    if (searchSectionString !== null && searchSectionString !== undefined && searchSectionString != "") {
        let filtered = questionList.filter(function(qid, indx, arr){
            //return (answered.includes(value) === false);
            const qData = getQuestionData(courseName, qid);
            //console.log(qData);
            if (qData.section.includes(searchSectionString)) {
                console.log(qData);
                console.log(qData.section);
                return true;
            };
            return false;
        });
        questionList = [...filtered];

    } else {

        const stats = getCourseStatistics(courseName)

        if (byUnanswered !== undefined) {
            let filtered = questionList.filter(function(qid, indx, arr){
                if (stats.questions[qid].total === 0) {
                    return true
                }
                return false
            });
            questionList = [...filtered];
        }

        if (byIncorrect !== undefined) {
            let filtered = questionList.filter(function(qid, indx, arr){
                const total = stats.questions[qid].total
                const incorrect = stats.questions[qid].incorrect
                let raverage = 1
                if ( incorrect >= 1) {
                    raverage = 1 - (incorrect / total)
                }

                if (stats.questions[qid].incorrect > 0 && average < .90 ) {
                    return true
                }
                return false
            });
            questionList = [...filtered];
        }

    }

    // select a random set of questions from the list
    let quizList = [];
    if ( questionList.length >= qCount ) {
        for (let i=0; i<qCount && i<questionList.length; i++) {
            const randomQuestion = questionList[Math.floor(Math.random() * questionList.length)];
            quizList.push(randomQuestion);

        };
    } else {
        quizList = [...questionList];
    };
    quizList.sort(compareVersions);

    const d = new Date();
    const started = d.getTime()
    const sessionid = uuidv4()
    const qidsjson = JSON.stringify(quizList)
    sql = "INSERT INTO sessions (sessionid, started, coursename, qidsjson) VALUES "
    sql += `('${sessionid}', '${started}', '${courseName}', '${qidsjson}')`
    console.log(sql)
    db.exec(sql)

    // start a session
    const thisSession = {
        "started": started,
        'finished': null,
        "sessionid": sessionid,
        "questions": [...quizList]
    };
    userSessions.push(thisSession);
    //console.log(thisSession);
    return res.json(thisSession);
});

/*****************************************************
 * API: get quiz results for all questions
*****************************************************/
app.get('/api/stats/:courseName', async function (req, res) {
    const courseName = req.params.courseName
    const stats = getCourseStatistics(courseName)
    return res.json(stats)
});


/*****************************************************
 * API: post session answer
*****************************************************/
app.post('/api/session/answer', function (req, res) {

    // clear cache on insert ...
    resultsCache = {};

    console.log(req.body);

    const thisDate = moment.utc().format('YYYY-MM-DDTHH:MM:SS')
    let sessionid = req.body.sessionid;
    const coursename = req.body.coursename;
    const questionid = req.body.questionid;
    const answer = req.body.answer;
    const choiceindex = req.body.choiceindex;

    // if there is no session, then this is an adhoc question result ...
    if (sessionid === null || sessionid === undefined) {
        sessionid = uuidv4()
    }

    // check if the answer is correct or not
    const qData = getQuestionData(coursename, questionid)
    let isCorrect = 0;
    if (choiceindex !== null && choiceindex !== undefined && choiceindex !== 'null') {
        if (choiceindex === qData.correct_choice_index) {
            isCorrect = 1;
        }
    } else {
        if ( answer === qData.answer ) {
            isCorrect = 1;
        }
    }

    let sql = "INSERT OR REPLACE INTO answers"
    sql += " (datetime, sessionid, coursename, questionid, answer, choiceindex, correct) VALUES"
    sql += "("
    sql += "'" + thisDate + "'"
    sql += " ,"
    sql += "'" + sessionid + "'"
    sql += " ,"
    sql += "'" + coursename + "'"
    sql += " ,"

    sql += "'" + questionid + "'"
    sql += " ,"

    sql += "'" + answer + "'"
    sql += " ,"

    if ( choiceindex !== null ) {
        sql += choiceindex.toString()
    } else {
        sql += 'null'
    }
    sql += " ,"

    sql += isCorrect

    sql += ")"
    console.log(sql);
    db.exec(sql);

    return res.json({'msg': 'ok'})
})

/*****************************************************
 * API: get quiz results
*****************************************************/
app.get('/api/results/:sessionid', async function (req, res) {
    const sessionid = req.params.sessionid
    let rows = []

    // https://stackoverflow.com/a/47963102
    rows = db.prepare(
        `SELECT * FROM sessions WHERE sessionid='${sessionid}'`
    ).all()
    console.log(rows)
    const sessionData = rows[0]
    let sessionQuestionIds = []
    let totalQuestions = 1
    if ( sessionData.qidsjson !== undefined ) {
        sessionQuestionIds = JSON.parse(sessionData.qidsjson)
        totalQuestions = sessionQuestionIds.length
    }

    // how many were answered?
    rows = db.prepare(
        `SELECT COUNT(*) FROM answers WHERE sessionid='${sessionid}'`
    ).all()
    console.log(rows)
    const totalAnswered = rows[0]['COUNT(*)']

    // how many were correct?
    rows = db.prepare(
        `SELECT COUNT(*) FROM answers WHERE sessionid='${sessionid}' AND correct=${boolTrue}`
    ).all()
    console.log(rows)
    const totalCorrect = rows[0]['COUNT(*)']

    // what was correct and what was incorrect
    rows = db.prepare(
        `SELECT questionid,correct FROM answers WHERE sessionid='${sessionid}'`
    ).all()
    console.log(rows)
    let correct = []
    let incorrect = []
    let unanswered = [...sessionQuestionIds]
    rows.forEach((row) => {
        if ( row.correct === boolTrue ) {
            correct.push(row.questionid)
        } else {
            incorrect.push(row.questionid)
        }

        const ix = unanswered.indexOf(row.questionid)
        unanswered.splice(ix, 1)
    })

    // what is the score?
    const score = (totalCorrect / totalQuestions ) * 100

    console.log(`sending results for ${sessionid} ...`)
    return res.json({
        'courseName': sessionData.coursename,
        'started': sessionData.started,
        sessionQuestionIds,
        totalAnswered,
        totalCorrect,
        totalQuestions,
        score,
        correct,
        incorrect,
        unanswered,
    })
})




app.get('/', (req, res) => res.send('Hello World!'))
app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`))
//db.close()
