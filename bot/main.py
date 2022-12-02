from fastapi import FastAPI, status, HTTPException
from dialogue_logic import  DialogueSystem
from db_manager import cursor as dbcur

app = FastAPI()
dsys = DialogueSystem()


@app.get("/dialogue")
def index(user_id: int, message: str = "/start"):
    user = dsys.get_user(user_id)
    if not user:
        user = dsys.add_user(user_id)
    from_dialogue = dsys.get_dialogue(user.dialogue_id)
   
    response_text = None
    
    answer_id = 0
    from_dialogue_id = 0 

    if message == "/start" or not from_dialogue:
        start_dialogue = dsys.get_dialogue(1)
        user.set_current_dialogue(start_dialogue)
        response_text = start_dialogue.text
    else:
        from_dialogue_id = from_dialogue.id
        success, transition = from_dialogue.get_possible_transition(message)
        if success:
            next_dialogue = dsys.get_dialogue(transition.dialogue_to)
            user.set_current_dialogue(next_dialogue)
            response_text = next_dialogue.text
            answer_id = transition.answer.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Не найдено соответствующего ответа на ввод пользователя.',
            )
            
    dsys.log_user_input(user.id, answer_id, message, from_dialogue_id, dsys.get_dialogue(user.dialogue_id).id)
    
    return {"user_id":user_id, "answer_id":answer_id,"response_text":response_text,"to_dialogue":dsys.get_dialogue(user.dialogue_id).id}

@app.get("/last_messages")
def index(user_id: int, count: int = 10):
    user = dsys.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Пользователь с user_id {user_id} не найден.',
        )
    dbcur.execute("SELECT * FROM user_logs WHERE user_id = %s ORDER BY send_date DESC LIMIT %s;", (user_id, count))
    q_result = dbcur.fetchall()
    
    data = []
    for row in q_result:
        data.append({
            "log_id":row[0],
            "answer_id":row[2],
            "sended_text":row[3],
            "from_dialogue":row[4],
            "to_dialogue":row[5],
            "send_date":row[6]
            })

    response = {
        "user_id":user_id,
        "count":count,
        "data":data    
    }

    return response