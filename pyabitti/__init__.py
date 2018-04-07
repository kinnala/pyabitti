import zipfile
import json
import io

class Identified():
    id = -1  # Unique id

    def _set_id(self, id):
        self.id = id
        return id + 1

class Question(Identified):
    displayNumber = "Question number as string"
    level = 1
    maxScore = -1  # The maximum amount of points
    type = "Question type: text, choicegroup"
    text = "The question"

    def __init__(self, question):
        self.displayNumber = question['displayNumber']
        self.id = question['id']
        self.level = question['level']
        self.type = question['type']
        self.text = question['text']
        self.maxScore = question['maxScore']

    def _export(self):
        out = {}
        out['displayNumber'] = self.displayNumber
        out['id'] = self.id
        out['level'] = self.level
        out['maxScore'] = self.maxScore
        out['type'] = self.type
        out['text'] = self.text
        return out

    def _set_displayNumber(self, displayNumber):
        self.displayNumber = displayNumber

    @staticmethod
    def factory(question):
        if question['type'] == 'text':
            return TextQuestion(question)
        elif question['type'] == 'choicegroup':
            return ChoiceQuestion(question)
        else:
            raise Exception("The question type '" + question['type'] + "' is not yet supported.")


class TextQuestion(Question):
    screenshotExpected = True

    def __init__(self, question):
        super(TextQuestion, self).__init__(question)
        self.screenshotExpected = question['screenshotExpected']

    def _export(self):
        out = super(TextQuestion, self)._export()
        out['screenshotExpected'] = self.screenshotExpected
        return out


class Option(Identified):
    text = "The option text"
    correct = False

    def __init__(self, option):
        self.id = option['id']
        self.text = option['text']
        self.correct = option['correct']

    def _export(self):
        out = {}
        out['id'] = self.id
        out['text'] = self.text
        out['correct'] = self.correct
        return out


class Choice(Identified):
    displayNumber = "Question number as string"
    type = "choice"
    text = "The question"
    breakAfter = False
    options = []

    def __init__(self, choice):
        self.displayNumber = choice['displayNumber']
        self.id = choice['id']
        self.type = choice['type']
        self.text = choice['text']
        self.breakAfter = choice['breakAfter']
        self.options = [Option(opt) for opt in choice['options']]

    def _export(self):
        out = {}
        out['displayNumber'] = self.displayNumber
        out['id'] = self.id
        out['type'] = self.type
        out['text'] = self.text
        out['breakAfter'] = self.breakAfter
        out['options'] = [option._export() for option in self.options]
        return out

    def _set_id(self, id):
        self.id = id
        cid = id + 1
        for opt in self.options:
            cid = opt._set_id(cid)
        return cid


class ChoiceQuestion(Question):
    choices = []

    def __init__(self, question):
        super(ChoiceQuestion, self).__init__(question)
        self.choices = [Choice(choice) for choice in question['choices']]

    def _export(self):
        out = super(ChoiceQuestion, self)._export()
        out['choices'] = [choice._export() for choice in self.choices]
        return out

    def _set_id(self, id):
        self.id = id
        cid = id + 1
        for choice in self.choices:
            cid = choice._set_id(cid)
        return cid

    def _set_displayNumber(self, displayNumber):
        self.displayNumber = displayNumber
        cid = 1
        for choice in self.choices:
            choice.displayNumber = displayNumber + "." + str(cid)
            cid += 1


class Exam():
    title = "Exam name"
    instruction = "Exam instructions"
    casForbidden = False
    questions = []

    attachments = {}  # key: filename, value: file contents

    def __init__(self, filename):
        self.load(filename)

    def load(self, filename):
        # read exam
        archive = zipfile.ZipFile(filename, 'r')
        rawdata = archive.read('exam-content.json')
        archive.close()

        data = json.load(io.BytesIO(rawdata))

        try:
            # try to read attachments
            attachdata = archive.read('attachments.zip')
            attacharchive = zipfile.ZipFile(io.BytesIO(attachdata))
            self.attachments = {name: attacharchive.read(name) for name in attacharchive.namelist()}
        except:
            print("No attachments in exam '" + filename + "'")
            # no attachments
            self.attachments = None

        self.title = data['title']
        self.instruction = data['instruction']
        self.casForbidden = data['casForbidden']
        self.questions = [Question.factory(q) for q in data['sections'][0]['questions']]

    def save(self, filename):
        # fix identifiers and display numbers
        self._fix_id()
        self._fix_displayNumber()

        # create dictionary for JSON dump
        out = {}
        out['title'] = self.title
        out['instruction'] = self.instruction
        out['casForbidden'] = self.casForbidden
        out['schemaVersion'] = "1.0"
        out['sections'] = [{}]
        out['sections'][0]['questions'] = [q._export() for q in self.questions]

        # save JSON dump to archive
        # TODO save attachments
        archive = zipfile.ZipFile(filename, 'w')
        archive.writestr("exam-content.json", json.dumps(out))
        archive.close()

    def _fix_id(self):
        cid = 0
        for q in self.questions:
            cid = q._set_id(cid)

    def _fix_displayNumber(self):
        qid = 1
        for q in self.questions:
            q._set_displayNumber(str(qid))
            qid += 1


