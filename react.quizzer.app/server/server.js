const compareVersions = require('compare-versions')
const express = require('express')
const moment = require('moment')
const app = express()
app.use(express.json());
const port = 4000
const fs = require('fs')

var sqlite3 = require('sqlite3').verbose()
var db = new sqlite3.Database(':memory:')
var db = new sqlite3.Database("./server/database/quizzer.db")

db.run('CREATE TABLE IF NOT EXISTS courses(name text)');
db.run('CREATE TABLE IF NOT EXISTS sessions(coursename text, sessionid text, datetime text)');
db.run('CREATE TABLE IF NOT EXISTS scores(datetime text, coursename text, sessionid text, score real)');
db.run('CREATE TABLE IF NOT EXISTS answers(datetime text, sessionid text, coursename text, questionid text, correct bool)');

let userSessions = [];

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
 * CONST: hash of courses and their questions
*****************************************************/
const courseList = fs.readdirSync('server/data/courses')
console.log(courseList)
let coursesFiles = {};
for (let i=0; i<courseList.length; i++) {
    let courseFileList = fs.readdirSync('server/data/courses/' + courseList[i])
    let courseQuestionList = courseFileList.map((filename) => {
        return removeFileExtension(filename);
    })
    coursesFiles[courseList[i]] = courseQuestionList
}

app.get('/api/courses', (req, res) => res.json(courseList))
app.get('/api/courses/:courseName', (req, res) => res.json(req.params))

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
    const filename = 'server/data/courses/' + req.params.courseName + '/' + req.params.questionID + '.json'

    // FIXME: return null data for null filenames
    console.log(filename)
    if (filename === undefined) {
        return res.json({
            'qid': req.params.questionID,
            'next': null,
            'previous': null,
            'filename': filename,
        })

    }

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
    let questionList = [...coursesFiles[req.params.courseName]]
    //let multiplechoice = req.query.multiplechoice
    //console.log(multiplechoice)
    multiplechoice = true;

    // get rid of already answered questions
    let answered = []
    let sql = "SELECT * FROM answers"
    sql += " WHERE "
    sql += "coursename=" + '"' + req.params.courseName + '"'
    try {
        await db.all(sql, (err, rows)=>{
            let rownum = 0;
            rows.forEach((row) => {
                //console.log(row)
                answered.push(row.questionid)
            })
        })
    } catch(error) {
        throw('error running ' + sql)
    }
    let filtered = questionList.filter(function(value, indx, arr){
        return (answered.includes(value) === false);
    });

    // clear out non-multiplechoice questions if requested ...
    filtered = filtered.filter(function(value, indx, arr){
        return (fileHasChoices(req.params.courseName, value));
    });

    questionList = filtered;

    // select a random set of questions from the list
    let quizList = [];
    for (let i=0; i<10; i++) {
        const randomQuestion = questionList[Math.floor(Math.random() * questionList.length)];
        //console.log('push', randomQuestion);
        quizList.push(randomQuestion);
    };
    //console.log('quizList', quizList);
    quizList.sort(compareVersions);
    //console.log('quizList.sorted ...', quizList);

    // start a session
    const d = new Date();
    const thisSession = {
        "started": d.getTime(),
        'finished': null,
        "sessionid": "00000",
        "questions": [...quizList]
    };
    userSessions.push(thisSession);
    //console.log(thisSession);
    return res.json(thisSession);
});

/*****************************************************
 * API: get quiz results for all questions
*****************************************************/
app.get('/api/results/:courseName', async function (req, res) {
    const courseName = req.params.courseName
    let questionList = [...coursesFiles[courseName]]
    questionList.sort(compareVersions);

    let questionStats = {};
    for (let i=0; i<questionList.length; i++) {
        questionStats[questionList[i]] = {
            coursename: courseName,
            questionid: questionList[i],
            total: 0,
            correct: 0,
            incorrect: 0
        }
    }

    let sql = "SELECT * FROM answers"
    sql += " WHERE "
    sql += "coursename=" + '"' + courseName + '"'

    try {
        await db.all(sql, (err, rows)=>{
            //console.log(err)
            //console.log(rows)

            let rownum = 0;
            rows.forEach((row) => {
                rownum += 1
                console.log(rownum)
                console.log(row)

                const qid = row.questionid
                console.log(qid)

                if ( questionStats[qid] ) { 
                    questionStats[qid].total += 1

                    if ( row.correct === 1 ) {
                        questionStats[qid].correct += 1
                    } else { 
                        questionStats[qid].incorrect += 1
                    }

                    console.log(questionStats[qid])
                }
            })

            //console.log(questionStats);
            //return res.json({'coursename': courseName, 'questionlist': questionList, 'stats': questionStats});
            //res.render('coursename': courseName, 'questionlist': questionList, 'stats': questionStats);
            res.send({'coursename': courseName, 'questionlist': questionList, 'stats': questionStats});

        })
    } catch(error) {
        throw('error running ' + sql)
    }

    //return res.json({'coursename': courseName, 'questionlist': questionList});
    //return res.json({'coursename': courseName, 'questionlist': questionList, 'stats': questionStats});
});

/*****************************************************
 * API: post quiz results
*****************************************************/
app.post('/api/results', function (req, res) {
    console.log('--------------------')
    //console.log(req)
    console.log(req.body)

    const thisDate = moment.utc().format('YYYY-MM-DDTHH:MM:SS')
    console.log(thisDate)

    //db.run('CREATE TABLE scores(coursename text, sessionid text, score real)');
    //db.run('CREATE TABLE answers(datetime text, sessionid text, coursename text, questionid text, correct bool)');

    let sql = "INSERT INTO scores (datetime, coursename, sessionid, score) VALUES"
    sql += "("
    sql += "'" + thisDate + "'"
    sql += " ,"
    sql += "'" + req.body.coursename + "'"
    sql += " ,"
    sql += "'" + req.body.sessionid + "'"
    sql += " ,"
    sql += req.body.score
    sql += ")"
    console.log(sql);
    db.run(sql);

    const allQuestions = req.body.correct.concat(req.body.incorrect);
    for (let i=0; i<allQuestions.length; i++) {
        console.log(i);
        const thisId = allQuestions[i]
        console.log(thisId)
        let isCorrect = false
        if (req.body.correct.includes(thisId)) {
            isCorrect = true
        }
        console.log(isCorrect);

        sql = "INSERT INTO answers (datetime, sessionid, coursename, questionid, correct) VALUES"
        sql += "("
        sql += "'" + thisDate + "'"
        sql += " ,"
        sql += "'" + req.body.sessionid + "'"
        sql += " ,"
        sql += "'" + req.body.coursename + "'"
        sql += " ,"
        sql += "'" + thisId + "'"
        sql += " ,"
        sql += isCorrect
        sql += ")"
        console.log(sql);
        db.run(sql);
    }

    return res.json({'msg': 'ok'})
});

app.get('/', (req, res) => res.send('Hello World!'))

app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`))

//db.close()
