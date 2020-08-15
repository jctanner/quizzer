import React from 'react';
import { useEffect, useState } from 'react';
import { Link, useHistory, useParams } from "react-router-dom";

import { InlineReport } from './Report';

function SessionPage() {
	let { sessionid } = useParams();
    let courseID = null;
    let questionIDs = [];
    let userAnswers = [];
    return (
         <InlineReport
            sessionid={ sessionid }
            courseName={ courseID }
            questionIDs={ questionIDs }
            userAnswers={ userAnswers }
        />
    );
}

export default SessionPage;
