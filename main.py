from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from model import Contact, LinkPrecedenceEnum
from schemas import IdentifyRequest, IdentifyResponse

app = FastAPI()
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/")
def root():
    return {"Identity_recon is working"}


@app.post("/identify", response_model=IdentifyResponse)
def identify_contact(payload: IdentifyRequest, db: Session = Depends(get_db)):
    email = payload.email
    phone = payload.phoneNumber
    #print(email, phone)
    # Find all contacts matching email or phone
    query = db.query(Contact)
    filters = []
    if email:
        filters.append(Contact.email == email)
    if phone:
        filters.append(Contact.phoneNumber == phone)
    if not filters:
        raise HTTPException(status_code=400, detail="At least one of email or phoneNumber must be provided.")

    contacts = query.filter(
        (Contact.email == email) | (Contact.phoneNumber == phone)
    ).all()

    # If no contacts, create new primary
    if not contacts:
        new_contact = Contact(
            email=email,
            phoneNumber=phone,
            linkPrecedence=LinkPrecedenceEnum.primary
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return {
            "contact": {
                "primaryContactId": new_contact.id,
                "emails": [email] if email else [],
                "phoneNumbers": [phone] if phone else [],
                "secondaryContactIds": []
            }
        }

    # Find all related contacts
    all_contacts = set(contacts)
    to_check = set(contacts)
    while to_check:
        c = to_check.pop()
        # Find all contacts linked to this one
        linked = db.query(Contact).filter(
            (Contact.linkedId == c.id) | (Contact.id == c.linkedId)
        ).all()
        for l in linked:
            if l not in all_contacts:
                all_contacts.add(l)
                to_check.add(l)

    all_contacts = list(all_contacts)

    # Find the primary contact ->oldest createdAt
    primary_contact = min(
        [c for c in all_contacts if c.linkPrecedence == LinkPrecedenceEnum.primary],
        key=lambda c: c.createdAt
    )

    # If new info-> create secondary
    emails = set()
    phones = set()
    for c in all_contacts:
        if c.email:
            emails.add(c.email)
        if c.phoneNumber:
            phones.add(c.phoneNumber)
    if (email and email not in emails) or (phone and phone not in phones):
        new_contact = Contact(
            email=email,
            phoneNumber=phone,
            linkPrecedence=LinkPrecedenceEnum.secondary,
            linkedId=primary_contact.id
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        all_contacts.append(new_contact)

    # Merge primaries if needed clashes 
    primaries = [c for c in all_contacts if c.linkPrecedence == LinkPrecedenceEnum.primary]
    if len(primaries) > 1:
        #oldest to primary
        primaries.sort(key=lambda c: c.createdAt)
        main_primary = primaries[0]
        for p in primaries[1:]:
            p.linkPrecedence = LinkPrecedenceEnum.secondary
            p.linkedId = main_primary.id
            db.add(p)
        db.commit()
        primary_contact = main_primary

    #response body 
    emails = []
    phones = []
    secondary_ids = []
    for c in all_contacts:
        if c.linkPrecedence == LinkPrecedenceEnum.primary:
            if c.email and c.email not in emails:
                emails.insert(0, c.email)
            if c.phoneNumber and c.phoneNumber not in phones:
                phones.insert(0, c.phoneNumber)
        else:
            if c.email and c.email not in emails:
                emails.append(c.email)
            if c.phoneNumber and c.phoneNumber not in phones:
                phones.append(c.phoneNumber)
            secondary_ids.append(c.id)

    return {
        "contact": {
            "primaryContactId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids
        }
    } 