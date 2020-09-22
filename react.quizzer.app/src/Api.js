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

    const resultApiUrl = '/api/session/answer';
    fetch(resultApiUrl, postOptions)
        .then(response => response.json());
}

export const getSessionResults = (sessionid) => {
    const sessionResultsUrl = '/api/results/' + sessionid;
    const qData = fetch(sessionResultsUrl).then(res => res.json())
    return qData;
}
