import hashlib
import json
import os

from docutils.nodes import section
import google.generativeai as gemini


def get_version():
    cwd = os.path.abspath(os.path.dirname(__file__))
    with open(f'{cwd}/version.json', 'r') as f:
        return json.load(f)['version']


def generate_questions(app, doc_tree, doc_name):
    questions_dir = f'{app.config.sphinx_ai_dir}/questions'
    model_name = 'gemini-1.5-flash'
    for node in doc_tree.traverse(section):
        xml = node.asdom().toxml()
        md5 = hashlib.md5(xml.encode('utf-8')).hexdigest()
        model = gemini.GenerativeModel(model_name)
        prompt = (
            'Generate a natural language question related to the text. '
            'Only output the question. Do not explain anything. '
            f'Query: {xml}'
        )
        response = model.generate_content(prompt)
        question = response.text
        with open(f'{questions_dir}/{md5}.json', 'w') as f:
            data = {
                'doc_name': doc_name,
                model_name: question
            }
            json.dump(data, f, indent=4)
    # TODO: Remove old data.


def setup(app):
    # API key setup
    app.add_config_value('sphinx_ai_gemini_api_key', None, 'html')
    if app.config.sphinx_ai_gemini_api_key is not None:
        gemini.configure(api_key=app.config.sphinx_ai_gemini_api_key)

    # Output directory setup
    default_dir = f'{app.confdir}/_sphinx-ai'
    app.add_config_value('sphinx_ai_dir', default_dir, 'html')
    out_dir = app.config.sphinx_ai_dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    app.add_config_value('sphinx_ai_questions', True, 'html')
    if app.config.sphinx_ai_questions:
        questions_dir = f'{out_dir}/questions'
        if not os.path.exists(questions_dir):
            os.makedirs(questions_dir)

    # Event hooks
    if app.config.sphinx_ai_questions:
        app.connect('doctree-resolved', generate_questions)

    # Extension runtime metadata required by Sphinx
    version = get_version()
    print('version', version)
    return {
        'version': version,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
