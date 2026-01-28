import streamlit as st

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from typing import Optional, List


class Person(BaseModel):
    name: Optional[str] = Field(default=None, description="人物の名前")
    age: Optional[int] = Field(default=None, description="年齢")

class Persons(BaseModel):
    persons: List[Person] = Field(default=[], description="人々")

st.write("start")

llm = ChatOllama(model="gpt-oss:20b", reasoning="low")
structured_llm = llm.with_structured_output(schema=Persons)

result = structured_llm.invoke("太郎は男性で25歳で一人暮らしです。次郎は今年33歳で、犬をかっています。三郎は1955年生まれです。今年は1977年です。")
print(result)  # Person(name="太郎", age=25)

st.write(str(result))
