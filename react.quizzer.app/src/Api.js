/*
app.post('/api/session/answer', function (req, res) {
    const session = req.body.session;
    const coursename = req.body.coursename;
    const questionid = req.body.questionid;
    const answer = req.body.answer;
    const choiceindex = req.body.choiceindex;
}
*/


export const postSessionAnswer = (sessionid, coursename, questionid, answer, choiceindex) => {
    const postOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            sessionid: sessionid,
            coursename: coursename,
            questionid: questionid,
            answer: answer,
            choiceindex: choiceindex
        })
    };

    console.log('postSessionAnswer', postOptions);
    const resultApiUrl = '/api/session/answer';
    fetch(resultApiUrl, postOptions)
        .then(response => response.json());
}

