//tag::emp[]
public class Employee {
    public static HazelcastJsonValue asJson(String surname) {
        return new HazelcastJsonValue("{ \"surname\": \"" + surname + "\" }");
    }
}
//end::emp[]