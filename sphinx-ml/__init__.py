import glob
import hashlib
import json
import os

from docutils.nodes import section
import google.generativeai as gemini


########## UTILITIES ##########


def compute_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


########## EMBEDDINGS ##########


def get_embeddings_dir_path(app):
    out_dir = app.config.sphinx_ml_out_dir
    return f'{out_dir}/embeddings'


def gather_old_hashes(embeddings_dir, doc_name):
    old_hashes = []
    for filename in os.listdir(embeddings_dir):
        if not filename.endswith('.json'):
            continue
        embedding_file_path = f'{embeddings_dir}/{filename}'
        print(embedding_file_path)
        with open(embedding_file_path, 'r') as f:
            data = json.load(f)  # TODO: Delete the file if it can't be loaded.
        if data['doc_name'] != doc_name:
            continue
        old_hashes.append(data['section_hash'])
    return old_hashes


def delete_old_embeddings(old_hashes, new_hashes, embeddings_dir):
    for old_hash in old_hashes:
        if old_hash in new_hashes:
            continue
        outdated_embedding_path = f'{embeddings_dir}/{old_hash}.json'
        os.remove(outdated_embedding_path)


def verify_embedding_files(embeddings_dir):
    # Make sure that all files can be loaded.
    # Maybe compare them against the expected schema, too.
    # This should be done once, during initial setup.
    pass


def update_embeddings(app, doc_tree, doc_name):
    embeddings_dir = get_embeddings_dir_path(app)
    old_hashes = gather_old_hashes(embeddings_dir, doc_name)
    new_hashes = []
    for node in doc_tree.traverse(section):
        section_xml = node.asdom().toxml()
        new_hash = compute_hash(section_xml)
        new_hashes.append(new_hash)
        if new_hash in old_hashes:
            continue
        response = gemini.embed_content(
            model='models/text-embedding-004',
            content=section_xml,
            task_type='SEMANTIC_SIMILARITY'
        )
        embedding = response['embedding'] if 'embedding' in response else None
        embedding_file_path = f'{embeddings_dir}/{new_hash}.json'
        with open(embedding_file_path, 'w') as f:
            data = {
                'doc_name': doc_name,
                'section_xml': section_xml,
                'section_hash': new_hash,
                'embedding': embedding
            }
            json.dump(data, f, indent=4)
    delete_old_embeddings(old_hashes, new_hashes, embeddings_dir)


########## SETUP ##########


def setup_api_keys(app):
    # Gemini
    app.add_config_value('sphinx_ml_gemini_api_key', None, 'html')
    if app.config.sphinx_ml_gemini_api_key is not None:
        gemini.configure(api_key=app.config.sphinx_ml_gemini_api_key)


def setup_output_directories(app):
    # Top-level output directory
    default_out_dir = f'{app.confdir}/_sphinx-ml'
    app.add_config_value('sphinx_ml_out_dir', default_out_dir, 'html')
    out_dir = app.config.sphinx_ml_out_dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    # TODO: Test that directory is created at default location.
    # TODO: Test that directory is created at custom location.
    # Embeddings output subdirectory
    embeddings_dir = get_embeddings_dir_path(app)
    if not os.path.exists(embeddings_dir):
        os.makedirs(embeddings_dir)
    # TODO: Test that directory is created.


def setup_event_handlers(app):
    app.connect('doctree-resolved', update_embeddings)


def setup_sphinx_metadata():
    cwd = os.path.abspath(os.path.dirname(__file__))
    with open(f'{cwd}/version.json', 'r') as f:
        version = json.load(f)['version']
    return {
        'version': version,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }


def setup(app):
    setup_api_keys(app)
    setup_output_directories(app)
    setup_event_handlers(app)
    return setup_sphinx_metadata()
