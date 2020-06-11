FROM rasa/rasa-sdk:1.10.1
WORKDIR /app
COPY actions/requirements-actions.txt ./

# Change to root to install dependancies
USER root
RUN pip install -r requirements-actions.txt
USER 1001

COPY ./actions /app/actions
COPY ./data /app/data
CMD ["start", "--actions", "actions.actions"]
